import re
import requests
import numpy as np

from io import BytesIO
from pydub import AudioSegment
from pydub.utils import make_chunks


from pyspark.sql import SparkSession, Row
from pyspark.sql.functions import *
from pyspark.sql.types import ArrayType, BinaryType, StringType, MapType

from pytubefix import YouTube
from pytubefix.cli import on_progress

from os import getenv, mkdir


APP_NAME = "UZBEK_SPEECH_TO_TEXT"
SPARK_PACKEGES = "spark.jars.packages"
SPARK_DRIVER = "org.postgresql:postgresql:42.7.4"

JDBC_DRIVER = "org.postgresql.Driver"
JDBC_USER = "postgres"
JDBC_USER_PASSWORD = "postgres"
JDBC_URL = "jdbc:postgresql://localhost:5432/myaudios_path"

JDBC_TABLE_AUDIO = "demo_stt_result_save"
JDBC_TABLE_YOUTUBE = "youtube_audio_to_text"

YOUTUBE_AUDIO_DIR = 'youtube'


class STT_Pipeline:
    def __init__(self, input, local_partition=250, stt_partition=3):
        # for local machine cpi (core i5-1340P × 16) default_partition = 250
        # for STT on cpu partition = 3

        classified_input = STT_Pipeline.classify_inputs(input)
        inputs = [
            {"source": source, "source_type" : type}
            for type in ['audio_files', 'youtube_urls']
            for source in classified_input[type]
        ]
        self.__jbdc_driver = JDBC_DRIVER
        self.__jdbc_user = JDBC_USER
        self.__jbdc_user_password = JDBC_USER_PASSWORD
        self.__jdbc_url = JDBC_URL
        
        self.__jbdc_table_audio = JDBC_TABLE_AUDIO
        self.__jbdc_table_youtube = JDBC_TABLE_YOUTUBE

        try:
            mkdir(YOUTUBE_AUDIO_DIR)
            print(f"Directory '{YOUTUBE_AUDIO_DIR}' created successfully.")
        except FileExistsError:
            print(f"Directory '{YOUTUBE_AUDIO_DIR}' already exists.")
        except PermissionError:
            print(f"Permission denied: Unable to create '{YOUTUBE_AUDIO_DIR}'.")
        except Exception as e:
            print(f"An error occurred: {e}")

        self.spark = SparkSession.builder \
            .appName(APP_NAME) \
            .config("spark.driver.memory", "12g") \
            .config("spark.jars.packages", "org.postgresql:postgresql:42.7.4") \
            .getOrCreate()
        self.spark.sparkContext.setLogLevel("ERROR")

        # Enable Adaptibe Query Execution (AQE) optimizer
        self.spark.conf.set("spark.sql.adaptive.enabled", "true")
        self.spark.conf.set("spark.sql.adaptive.optimizerEnabled", "true")

        # Enable Apache Arrow to speed up data transfer between Spark and Python
        self.spark.conf.set("spark.sql.execution.arrow.pyspark.enabled", "true")
       
        buffer_udf = udf(STT_Pipeline.to_buffer, MapType(StringType(), ArrayType(BinaryType())))

        chunks_to_text_udf = udf(STT_Pipeline.bufChunkstoText, StringType())

        self.dataFrame = self.spark.createDataFrame(inputs)

        self.df_audio = None
        self.df_youtube = None
        
        # Spliting audio into chunks
        self.dataFrame = self.dataFrame.withColumn("buff_list", buffer_udf(col('source')))

        # Changing the value of partitions
        self.dataFrame = self.dataFrame.repartition(stt_partition)
        
        # Exploding the list of chunks
        self.dataFrame = self.dataFrame.withColumn(
            'absolute_path', explode(map_keys(self.dataFrame.buff_list))
        )
        
        self.dataFrame = self.dataFrame.withColumn(
            'buff_list', explode(map_values(self.dataFrame.buff_list))
        )
        
        self.dataFrame = self.dataFrame.withColumn(
            'buff_list', explode(col('buff_list'))
        )

        # Recieving the text from the audio
        self.dataFrame = self.dataFrame.withColumn('transcription', chunks_to_text_udf(col('buff_list')))
        
        self.dataFrame = self.dataFrame.groupBy('source', 'source_type', 'absolute_path') \
            .agg(concat_ws(' ', collect_list(col('transcription'))).alias('transcription'))
        
        # Changing the value of partitions
        self.dataFrame = self.dataFrame.repartitionByRange(local_partition, 'transcription')
        
        self.dataFrame.show()
    
    @staticmethod
    def classify_inputs(inputs):
        youtube_urls = []
        audio_files = []
        
        # Define a regex pattern to match YouTube URLs
        youtube_pattern = re.compile(
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)(/[\w-]*)?(\?[\w=&]*)?'
        )
        
        # Classify each input
        for item in inputs:
            if youtube_pattern.match(item):
                youtube_urls.append(item)
            else:
                audio_files.append(item)
        
        return {'audio_files': audio_files, 'youtube_urls': youtube_urls}
    
    @staticmethod
    def to_buffer(string):
        youtube_pattern = re.compile(
            r'(https?://)?(www\.)?(youtube\.com|youtu\.be)(/[\w-]*)?(\?[\w=&]*)?'
        )
        if youtube_pattern.match(string):
            return STT_Pipeline.youtubeToBufChunks(string)
        return STT_Pipeline.audioToBufChuncks(string) 
    
    @staticmethod
    def audioToBufChuncks(input_file):
        """
        Process the input audio file: convert to target format, split into chunks, and return buffers.
        :param input_file: Path to the input audio file
        :return: List of buffers for each audio chunk
        """
        target_format = "wav"
        sample_rate = 16000
        chunk_duration = 30
        # Load the audio file
        audio = AudioSegment.from_file(input_file)
        
        # Convert to target format and sample rate
        audio = audio.set_frame_rate(sample_rate).set_channels(1)
        
        # Split audio into chunks
        chunk_length_ms = chunk_duration * 1000  # Convert seconds to milliseconds
        chunks = make_chunks(audio, chunk_length_ms)        
        
        # Convert chunks to buffer-like objects
        buffers = []
        for chunk in chunks:
            buffer = BytesIO()
            chunk.export(buffer, format=target_format)
            buffer.seek(0)  # Reset buffer position
            buffers.append(buffer.read())
        return {'-' : buffers}

    @staticmethod
    def youtubeToBufChunks(url):
        target_format = "wav"
        sample_rate = 16000
        chunk_duration = 30
        # Step 1: Download the audio stream
        yt = YouTube(url)
        audio_stream = yt.streams.get_audio_only()
        
        path = audio_stream.download(output_path=YOUTUBE_AUDIO_DIR)
        
        # Save the audio to a temporary buffer
        audio_buffer = BytesIO()
        audio_stream.stream_to_buffer(audio_buffer)
        audio_buffer.seek(0)  # Reset the buffer position
        
        # Step 2: Convert to pydub AudioSegment
        audio = AudioSegment.from_file(audio_buffer)
        audio = audio.set_frame_rate(sample_rate).set_channels(1)

        chunk_length_ms = chunk_duration * 1000  # Convert seconds to milliseconds
        chunks = make_chunks(audio, chunk_length_ms) 
        
        # Convert chunks to buffer-like objects
        buffers = []
        for chunk in chunks:
            buffer = BytesIO()
            chunk.export(buffer, format=target_format)
            buffer.seek(0)  # Reset buffer position
            buffers.append(buffer.getvalue())
        return {path : buffers}
    
    @staticmethod
    def bufChunkstoText(buf):
        arr = np.array(buf)
        buffer = arr.tobytes()
        
        files = {'audio': buffer}
        key = "STT_API"
        api_env = getenv(key)
        response = requests.post(api_env, files=files)

        text = response.json()['transcription']
        return text
    
    def to_csv(self, path):
        self.dataFrame.write.option('header', True).csv(path)
    
    def toPandas(self):
        return self.dataFrame.toPandas()
    
    def save(self, save_mode='append'): # optimize this part
        self.df_audio = self.dataFrame.filter(col('source_type') == 'audio_files')
        self.df_youtube = self.dataFrame.filter(col("source_type") == "youtube_urls")

        self.df_audio = self.df_audio.select(
            col('source').alias('audio_path'),
            col('transcription')
        )

        self.df_youtube = self.df_youtube.select(
            col('source').alias('youtube'),
            col('absolute_path'),
            col('transcription')
        )

        properties = {
            "user": self.__jdbc_user,
            "password": self.__jbdc_user_password,
            "driver": self.__jbdc_driver
        }

        self.df_audio.write.jdbc(
            url=self.__jdbc_url,
            table=self.__jbdc_table_audio,
            mode=save_mode,
            properties=properties
        )

        self.df_youtube.write.jdbc(
            url=self.__jdbc_url,
            table=self.__jbdc_table_youtube,
            mode=save_mode,
            properties=properties
        )
    
    def set_url(self, url):
        self.__jdbc_url  = url

    def set_user(self, user):
        self.__jdbc_user = user
    
    def set_password(self, password):
        self.__jbdc_user_password  = password
    
    def set_table_audio(self, table):
        self.__jbdc_table_audio  = table
    
    def set_table_youtube(self, table):
        self.__jbdc_table_youtube  = table
