"""File operation tools for downloading and reading files."""

import os
import re
import tempfile
import requests
from pathlib import Path
from typing import Optional

from llama_index.core.tools import FunctionTool
from config import get_settings
from config.logging_config import get_logger

# Setup logging
logger = get_logger(__name__)
settings = get_settings()


def download_file(task_id: str, save_dir: Optional[str] = None) -> str:
    """
    Download a file associated with a GAIA task.
    
    Args:
        task_id: The GAIA task ID
        save_dir: Optional directory to save the file (default: temp directory)
    
    Returns:
        Path to the downloaded file or error message
    """
    try:
        url = f"{settings.api.gaia_api_url}/files/{task_id}"
        logger.info(f"Downloading file for task: {task_id}")
        
        response = requests.get(
            url,
            timeout=settings.tool.file_download_timeout
        )
        response.raise_for_status()
        
        # Determine filename from Content-Disposition or use task_id
        filename = task_id
        if 'Content-Disposition' in response.headers:
            content_disp = response.headers['Content-Disposition']
            filename_match = re.search(r'filename="?([^"]+)"?', content_disp)
            if filename_match:
                filename = filename_match.group(1)
        
        # Save to specified directory or temp directory
        if save_dir:
            file_path = Path(save_dir) / filename
        else:
            temp_dir = tempfile.gettempdir()
            file_path = Path(temp_dir) / "gaia_files" / filename
        
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)
        
        logger.info(f"File downloaded to: {file_path}")
        return str(file_path)
    
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 404:
            return f"No file found for task {task_id}"
        logger.error(f"HTTP error downloading file: {e}")
        return f"Error downloading file: HTTP {e.response.status_code}"
    
    except Exception as e:
        logger.error(f"File download error: {e}")
        return f"Error downloading file for task {task_id}: {str(e)}"


def read_file(file_path: str) -> str:
    """
    Read and extract text from various file formats.
    
    Args:
        file_path: Path to the file to read
    
    Returns:
        Extracted text content or error message
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return f"File not found: {file_path}"
        
        logger.info(f"Reading file: {file_path}")
        
        extension = path.suffix.lower()
        max_chars = settings.tool.file_read_max_chars
        
        # Text files
        if extension in ['.txt', '.md', '.csv', '.json', '.xml', '.html', '.log']:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read(max_chars)
            return content
        
        # PDF files
        elif extension == '.pdf':
            try:
                import pypdf
                with open(path, 'rb') as f:
                    pdf_reader = pypdf.PdfReader(f)
                    text = []
                    # Read up to 20 pages
                    for page in pdf_reader.pages[:20]:
                        text.append(page.extract_text())
                    full_text = "\n\n".join(text)
                    return full_text[:max_chars]
            except ImportError:
                return "pypdf not installed. Run: pip install pypdf"
            except Exception as e:
                return f"Error reading PDF: {str(e)}"
        
        # Excel files
        elif extension in ['.xlsx', '.xls']:
            try:
                import pandas as pd
                df = pd.read_excel(path)
                return df.to_string()[:max_chars]
            except ImportError:
                return "pandas or openpyxl not installed. Run: pip install pandas openpyxl"
            except Exception as e:
                return f"Error reading Excel: {str(e)}"
        
        # CSV files  
        elif extension == '.csv':
            try:
                import pandas as pd
                df = pd.read_csv(path)
                return df.to_string()[:max_chars]
            except ImportError:
                return "pandas not installed. Run: pip install pandas"
            except Exception as e:
                return f"Error reading CSV: {str(e)}"
        
        # Word documents
        elif extension in ['.docx', '.doc']:
            try:
                import docx
                doc = docx.Document(path)
                text = "\n".join([para.text for para in doc.paragraphs])
                return text[:max_chars]
            except ImportError:
                return "python-docx not installed. Run: pip install python-docx"
            except Exception as e:
                return f"Error reading Word document: {str(e)}"
        
        # Image files
        elif extension in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff']:
            try:
                from PIL import Image
                img = Image.open(path)
                info = (
                    f"Image: {path.name}\n"
                    f"Format: {img.format}\n"
                    f"Size: {img.size[0]}x{img.size[1]} pixels\n"
                    f"Mode: {img.mode}\n"
                    f"File size: {path.stat().st_size / 1024:.2f} KB"
                )
                return info
            except ImportError:
                return "PIL not installed. Run: pip install pillow"
            except Exception as e:
                return f"Error reading image: {str(e)}"
        
        else:
            return f"Unsupported file type: {extension}"
    
    except Exception as e:
        logger.error(f"File reading error: {e}")
        return f"Error reading file {file_path}: {str(e)}"


# Create FunctionTool instances
file_download_tool = FunctionTool.from_defaults(
    fn=download_file,
    name="download_file",
    description=(
        "Download a file associated with a GAIA task using the task_id. "
        "Returns the path to the downloaded file. "
        "Use this when the question mentions a file or requires file analysis. "
        "After downloading, use read_file to read the content."
    )
)

file_reader_tool = FunctionTool.from_defaults(
    fn=read_file,
    name="read_file",
    description=(
        "Read and extract text content from various file formats. "
        "Supports: TXT, PDF, CSV, Excel (XLSX/XLS), Word (DOCX), JSON, XML, HTML, images. "
        "For images, returns basic information (dimensions, format). "
        "Use this after downloading a file to read its contents."
    )
)


# Export tools
FILE_TOOLS = [file_download_tool, file_reader_tool]

