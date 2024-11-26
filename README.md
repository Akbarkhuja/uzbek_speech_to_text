Here is the documentation for the `STT_Pipeline` class. The documentation includes an overview, constructor description, method explanations, and usage examples.

---

# **STT_Pipeline Documentation**

## **Overview**
The `STT_Pipeline` class processes audio files and YouTube videos for speech-to-text (STT) transcription. It uses Apache Spark for distributed processing and supports splitting audio into manageable chunks, transcribing them via an API, and storing the results in a PostgreSQL database.

---

## **Class Initialization**
```python
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

---

This documentation provides a comprehensive guide for users to understand and utilize the `STT_Pipeline` class effectively. Let me know if you'd like further customization!
