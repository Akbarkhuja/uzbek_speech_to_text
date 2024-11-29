Here is the documentation for the `STT_Pipeline` class. The documentation includes an overview, constructor description, method explanations, and usage examples.

---

# **STT_Pipeline Documentation**

## **Overview**
The `STT_Pipeline` class processes audio files and YouTube videos for speech-to-text (STT) transcription. It uses Apache Spark for distributed processing and supports splitting audio into manageable chunks, transcribing them via an API, and storing the results in a PostgreSQL database.

---

## **Prerequisites**
- **Installation of Apache Spark and PySpark:**
  - [Installation Guide](https://www.datacamp.com/tutorial/installation-of-pyspark)

- **PostgreSQL:**
  - Go the [page](https://www.postgresql.org/download/), choose your Linux distribution and follow the instructions
    
  - start PostgreSQL:
    ``` console
    sudo su - postgres
    ```
    
    ``` console
    psql
    ```
  
  - create a user the name "postgres" and with the password "postgres":
    ``` console
    alter user postgres with password 'postgres'; 
    ```
  
  - start the user:
    ``` console
    \du
    ```
    
  - create a database with the name "myaudios_path"
    ``` console
    create database myaudios_path;
    ```
    
  - in the same database create 2 tables:
    ``` sql
    CREATE TABLE demo_stt_result_save (
    audio_path TEXT NOT NULL,          -- Source of the audio file
    transcription TEXT NOT NULL    -- Transcribed text
    );
    ```
    
    ``` sql
    CREATE TABLE youtube_audio_to_text (
    youtube TEXT NOT NULL,          -- Source of the audio file
    absolute_path TEXT NOT NULL,
    transcription TEXT NOT NULL    -- Transcribed text
    );
    ```
    
- **Requirements:**
- open a new window of terminal and lauch the following command:
  ```console
  git clone https://github.com/Akbarkhuja/uzbek_speech_to_text.git
  ```
- Enter the directory:
  ```console
  cd uzbek_speech_to_text
  ```
  
  - install the requirements:
  ```console
  pip install -r requirements.txt
  ```
  
- **Export the environment variable:**
  - set the STT_API environment variable, which stores the URL of your STT API
    ```console
    export STT_API=your_stt_api_url
    ```
  - check
    ```console
    echo $STT_API
    ```
- **Launch:**
  ``` console
  python test.py
  ```
---

## **Class Initialization**
```python
from uzbek_speech_to_text_converter import STT_Pipeline

STT_Pipeline(input, local_partition=250, stt_partition=3)
```

### **Parameters**
- **input** (`list` of `str`): A list of input sources, either file paths to audio files or YouTube URLs.
- **local_partition** (`int`, optional): Number of partitions for local processing (default is `250`).
- **stt_partition** (`int`, optional): Number of partitions for speech-to-text processing (default is `3`).

---

## **Attributes**
- `dataFrame`: The primary Spark DataFrame containing processed audio or YouTube data.
- `spark`: The Spark session used for distributed processing.

---

## **Methods**

### **Static Methods**
#### **classify_inputs(inputs)**
Classifies input sources into YouTube URLs or audio file paths.

- **Parameters:**  
  - `inputs` (`list` of `str`): A list of input sources.
- **Returns:**  
  - `dict`: A dictionary with keys `'audio_files'` and `'youtube_urls'` mapping to respective lists of sources.

---

#### **to_buffer(string)**
Determines whether the input is a YouTube URL or an audio file and processes it accordingly.

- **Parameters:**  
  - `string` (`str`): Input source (audio file path or YouTube URL).
- **Returns:**  
  - `dict`: A dictionary containing audio chunks in buffer form.

---

#### **audioToBufChuncks(input_file)**
Processes an audio file: converts it to a standard format, splits it into chunks, and returns buffers.

- **Parameters:**  
  - `input_file` (`str`): Path to the audio file.
- **Returns:**  
  - `dict`: A dictionary containing buffers for each audio chunk.

---

#### **youtubeToBufChunks(url)**
Downloads and processes YouTube audio streams: converts to standard format, splits into chunks, and returns buffers.

- **Parameters:**  
  - `url` (`str`): YouTube video URL.
- **Returns:**  
  - `dict`: A dictionary containing buffers for each audio chunk.

---

#### **bufChunkstoText(buf)**
Sends an audio buffer to the speech-to-text API and returns the transcribed text.

- **Parameters:**  
  - `buf` (`binary`): A binary buffer of an audio chunk.
- **Returns:**  
  - `str`: Transcription of the audio chunk.

---

### **Instance Methods**
#### **to_csv(path)**
Saves the processed DataFrame as a CSV file.

- **Parameters:**  
  - `path` (`str`): File path to save the CSV.

---

#### **toPandas()**
Converts the processed Spark DataFrame to a Pandas DataFrame.

- **Returns:**  
  - `pandas.DataFrame`: A Pandas DataFrame containing the data.

---

#### **save(save_mode='append')**
Saves the results to a PostgreSQL database.

- **Parameters:**  
  - `save_mode` (`str`, optional): Save mode for the database (`'append'` by default).

---

#### **set_url(url)**
Sets the PostgreSQL JDBC URL.

- **Parameters:**  
  - `url` (`str`): New JDBC URL.

---

#### **set_user(user)**
Sets the PostgreSQL user.

- **Parameters:**  
  - `user` (`str`): New username.

---

#### **set_password(password)**
Sets the PostgreSQL password.

- **Parameters:**  
  - `password` (`str`): New password.

---

#### **set_table_audio(table)**
Sets the table name for saving audio file transcriptions.

- **Parameters:**  
  - `table` (`str`): New table name.

---

#### **set_table_youtube(table)**
Sets the table name for saving YouTube transcriptions.

- **Parameters:**  
  - `table` (`str`): New table name.

---

## **Usage Example**
```python
from uzbek_speech_to_text_converter import STT_Pipeline

# Input: List of YouTube URLs and audio file paths
inputs = ["https://youtu.be/example", "/path/to/audio.mp3"]

# Initialize the pipeline
pipeline = STT_Pipeline(inputs)

# Save transcriptions to a CSV
pipeline.to_csv("/path/to/output.csv")

# Save results to PostgreSQL
pipeline.save()

# Convert to Pandas DataFrame
df = pipeline.toPandas()
print(df.head())
```

- Also execute test.py in the directory of the project:
  ``` console
  python test.py
  ```
  
  and see the result by executing the following commands by lauching postgres:
  ```
  - start PostgreSQL:
    ``` console
    sudo su - postgres
    ```
    
    ``` console
    psql
    ```
  
  - create a user the name "postgres" and with the password "postgres":
    ``` console
    alter user postgres with password 'postgres'; 
    ```
  
  - start the user:
    ``` console
    \du
    ```
  - check the results:
    ``` console
    select * from demo_stt_result_save;
    ```

    ``` console
    select * from youtube_audio_to_text;
    ```

---

This documentation provides a comprehensive guide for users to understand and utilize the `STT_Pipeline` class effectively. Let me know if you'd like further customization!
