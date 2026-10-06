TRUEVISION: A Digital Forensics Framework

**TrueVision** is a unified digital forensic framework designed to verify the authenticity of text, images, and structured documents[cite: 2]. As artificial intelligence and machine learning advance, modern tools can generate realistic text, manipulate images, and modify digital documents with minimal effort, introducing serious challenges related to authenticity and digital integrity[cite: 2]. 

While traditional verification tools typically focus on a single content type, TrueVision addresses the need for a multi-modal framework by integrating **machine learning**, **deep learning**, **metadata analysis**, and **cryptographic hashing** techniques within a modular architecture[cite: 2].

✨ Key Features

* **Unified Multi-Modal Framework:** Detects forgery across images, text, and documents within a single, secure web-based platform[cite: 3, 5].
* **Image Authentication Module:** Analyzes uploaded images or images extracted from documents for signs of manipulation[cite: 26]. It utilizes a Convolutional Neural Network (CNN) to classify images as authentic or manipulated, extracting spatial features to identify tampering (like splicing and copy-move operations) and AI-generated content[cite: 18, 26]. It also employs Error Level Analysis (ELA) for pixel-level inconsistencies[cite: 21].
* **Text and Document Verification:** Evaluates textual content to determine originality and detect AI-generated writing[cite: 19]. This module uses similarity-based comparison for plagiarism detection and a supervised machine learning classifier (including BERT Large Language Models) to analyze linguistic patterns for AI generation[cite: 19, 20].
* **Metadata Inspection:** Analyzes document properties (such as author name, timestamps, device ID, and GPS) to identify inconsistencies that may indicate structural tampering[cite: 20].
* **File-Level Integrity Validation:** Implements cryptographic hashing mechanisms to ensure file-level integrity verification and detect binary-level modifications[cite: 4, 5].
* **Decentralized Reporting:** Each module independently generates and presents verification results to prevent ambiguity[cite: 19]. The system provides structured findings, authenticity scores, highlighted suspicious regions, and downloadable reports[cite: 19, 28].

 🏗️ System Architecture

TrueVision adopts a structured, modular workflow[cite: 22]. Users upload content (text, image, or PDF), which first passes through a **File Module** for format validation and metadata extraction[cite: 22]. The content is then routed to specific analysis modules: **Text & Document Analysis** or **Image Processing**[cite: 22]. These independent modules feed their outputs into a **Decision & Reporting** component that generates an authenticity assessment and highlights anomalies, displaying the final outcomes on an interactive user dashboard[cite: 22, 28]
<img width="588" height="660" alt="image" src="https://github.com/user-attachments/assets/bff9d28e-a6d6-4702-ba3c-d8cf01e6e260" />


 💻 Technology Stack

* **Web Framework:** Django[cite: 34]
* **Programming Language:** Python 3.8+[cite: 34]
* **Machine Learning & Deep Learning:** TensorFlow, Scikit-learn[cite: 34]
* **Image Processing:** OpenCV[cite: 34]
* **Data Processing:** NumPy, Pandas[cite: 35]
* **Document Processing:** PyPDF2, PDFMiner, python-docx[cite: 35]

<img width="588" height="660" alt="image" src="https://github.com/user-attachments/assets/06eb8960-6921-40bb-943a-79adb40a372d" />
<img width="859" height="379" alt="image" src="https://github.com/user-attachments/assets/fc859420-f591-412e-be44-a3045cc2733e" />
<img width="848" height="328" alt="image" src="https://github.com/user-attachments/assets/c4c3d9ec-49ea-4aa1-98f6-050428cd070e" />
<img width="844" height="480" alt="image" src="https://github.com/user-attachments/assets/b30da171-33c9-4cb3-93e6-c2c7008171fa" />
<img width="747" height="453" alt="image" src="https://github.com/user-attachments/assets/b4e69d7a-f0d3-4929-8e44-551b1efdf57b" />



