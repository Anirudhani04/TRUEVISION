 TRUEVISION: A Digital Forensics Framework
"A unified multi-modal system for detecting image forgery, text plagiarism and AI-generated content"

 Overview :
TrueVision is a comprehensive digital forensic framework designed to verify the authenticity of text, images, and structured documents. As artificial intelligence and machine learning advance, modern tools can generate realistic text, manipulate images, and modify digital documents with minimal effort. This introduces serious challenges related to authenticity, trust, and digital integrity across academic, journalistic, and legal environments.

While traditional verification tools typically focus on a single content type, TrueVision addresses the need for a multi-modal framework. It integrates machine learning, deep learning, metadata analysis, and cryptographic hashing techniques within a modular, web-based architecture to provide reliable, explainable, and automated forensic analysis.

✨ Key Features :
1) Unified Multi-Modal Framework: Detects forgery across images, text, and structured documents within a single, secure platform, eliminating the need for fragmented, single-purpose tools.

2) Image Authentication Module: Analyzes uploaded images (or images extracted from documents) for signs of sophisticated manipulation. It utilizes Convolutional Neural Networks (CNNs) and Error Level Analysis (ELA) to extract spatial features and identify tampering techniques like splicing, copy-move operations, and synthetic AI generation.

3) Text and Document Verification: Evaluates textual content to determine originality and detect AI-generated writing. This module uses similarity-based comparison for plagiarism detection alongside supervised machine learning classifiers (including BERT-based models) to analyze linguistic patterns and probabilistic features.

4) Metadata & Structural Inspection: Analyzes document properties (such as author names, creation timestamps, device IDs, and GPS data) to identify inconsistencies that may indicate structural tampering or hidden alterations.

5) File-Level Integrity Validation: Implements robust cryptographic hashing mechanisms to ensure file-level integrity, instantly detecting unauthorized binary-level modifications.

6) Decentralized & Explainable Reporting: Each module independently generates and presents its verification results to prevent ambiguity. The system provides structured findings, clear authenticity scores, highlighted suspicious regions, and downloadable PDF reports for auditing.

System Architecture :
TrueVision adopts a structured, modular workflow designed for scalability and precision:

Input & Validation (File Module): Users upload content (Text, Image, or PDF). The system performs format validation, cleans the data, and extracts embedded metadata.

Routing: The validated content is intelligently routed to the appropriate analysis engine.

Parallel Processing:

Text & Document Analysis: Executes AI-text detection, plagiarism similarity checks, OCR (if needed), and metadata consistency verification.

Image Processing: Executes forgery detection (splicing/copy-move), noise inconsistency checks, and deepfake/AI-generation analysis.

Decision & Reporting: Outputs from the independent modules are processed to generate a final authenticity assessment, which is then visualized on an interactive user dashboard and securely logged in the database.

<img width="588" height="660" alt="image" src="https://github.com/user-attachments/assets/0fdc3632-628e-4222-982e-f49b3c6d68b5" />


 Technology Stack :
Backend & Framework

Python 3.8+ – Core programming language

Django – Web framework and backend routing

SQLite / PostgreSQL – Database management

Machine Learning & Forensics :

TensorFlow / Keras – Deep learning models (CNNs) for image forensics

Scikit-learn – Supervised machine learning algorithms for text classification

Transformers (Hugging Face) – BERT LLM integration for semantic analysis

Data & File Processing :

OpenCV – Image preprocessing, ELA, and spatial feature extraction

NumPy & Pandas – Numerical computations and structured data handling

PyPDF2 & PDFMiner – PDF parsing and document content extraction

python-docx – Handling DOCX file structures

<img width="854" height="373" alt="image" src="https://github.com/user-attachments/assets/dd9053c0-93e3-4bee-808c-7491e1e28aca" />

<img width="859" height="379" alt="image" src="https://github.com/user-attachments/assets/fc859420-f591-412e-be44-a3045cc2733e" />

<img width="848" height="328" alt="image" src="https://github.com/user-attachments/assets/c4c3d9ec-49ea-4aa1-98f6-050428cd070e" />

<img width="844" height="480" alt="image" src="https://github.com/user-attachments/assets/b30da171-33c9-4cb3-93e6-c2c7008171fa" />




