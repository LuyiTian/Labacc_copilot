"""File conversion module for automatic document processing.

This module handles automatic conversion of uploaded files (PDF, Office docs) 
to Markdown format for easier processing by the AI agent.
"""

import asyncio
import json
import logging
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class FileConversionPipeline:
    """Handles automatic file conversion on upload."""
    
    def __init__(self, project_root: str):
        """Initialize the conversion pipeline.
        
        Args:
            project_root: Root directory for all projects
        """
        self.project_root = Path(project_root)
        
        # Lazy import conversion libraries to avoid startup overhead
        self._markitdown = None
        self._mineru_available = False
        self._mineru_cmd = "mineru"  # Default, will be updated in check
        self._check_mineru_availability()
    
    def _check_mineru_availability(self):
        """Check if MinerU v2 is available."""
        try:
            # Check for mineru CLI command
            import subprocess
            import sys
            
            # Try direct venv path first
            venv_mineru = Path(sys.prefix) / "bin" / "mineru"
            if venv_mineru.exists():
                self._mineru_cmd = str(venv_mineru)
            else:
                # Fallback to system mineru
                self._mineru_cmd = "mineru"
            
            result = subprocess.run(
                [self._mineru_cmd, "--version"],
                capture_output=True,
                text=True,
                timeout=15  # Increased timeout for model loading
            )
            if result.returncode == 0 and "mineru" in result.stdout.lower():
                self._mineru_available = True
                logger.info(f"MinerU v2 is available at {self._mineru_cmd}")
            else:
                self._mineru_available = False
                logger.warning("MinerU not available or not working properly")
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            self._mineru_available = False
            logger.warning(f"MinerU not available: {e}")
    
    def _get_markitdown(self):
        """Lazy load MarkItDown."""
        if self._markitdown is None:
            try:
                from markitdown import MarkItDown
                self._markitdown = MarkItDown()
                logger.info("MarkItDown loaded successfully")
            except ImportError as e:
                logger.error(f"Failed to import MarkItDown: {e}")
                raise RuntimeError("MarkItDown not available. Install with: pip install markitdown")
        return self._markitdown
    
    def needs_conversion(self, filename: str) -> bool:
        """Check if a file needs conversion based on its extension.
        
        Args:
            filename: Name of the file
            
        Returns:
            True if file needs conversion, False otherwise
        """
        convertible_extensions = {
            # Office formats
            '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
            # PDF
            '.pdf',
            # Web formats
            '.html', '.htm',
            # Other document formats
            '.rtf', '.odt', '.odp', '.ods'
        }
        
        return Path(filename).suffix.lower() in convertible_extensions
    
    async def convert_office_to_markdown(self, file_path: Path, output_path: Path) -> bool:
        """Convert Office document to Markdown using MarkItDown.
        
        Args:
            file_path: Path to the Office document
            output_path: Path where to save the Markdown
            
        Returns:
            True if conversion successful, False otherwise
        """
        try:
            # Get MarkItDown instance
            markitdown = self._get_markitdown()
            
            # Convert to markdown
            result = await asyncio.to_thread(
                markitdown.convert,
                str(file_path)
            )
            
            # Save the markdown content
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            logger.info(f"Successfully converted {file_path.name} to Markdown")
            return True
            
        except Exception as e:
            logger.error(f"Failed to convert Office file {file_path}: {e}")
            return False
    
    async def convert_pdf_to_markdown(self, file_path: Path, output_path: Path) -> bool:
        """Convert PDF to Markdown using MinerU or fallback to MarkItDown.
        
        Args:
            file_path: Path to the PDF file
            output_path: Path where to save the Markdown
            
        Returns:
            True if conversion successful, False otherwise
        """
        # Try MinerU v2 first if available (better quality for complex PDFs)
        if self._mineru_available:
            try:
                import subprocess
                
                # Create temporary directory for MinerU output
                with tempfile.TemporaryDirectory() as temp_dir:
                    temp_dir_path = Path(temp_dir)
                    output_dir = temp_dir_path / "mineru_output"
                    output_dir.mkdir()
                    
                    # Run MinerU CLI command
                    cmd = [
                        self._mineru_cmd,
                        "-p", str(file_path),
                        "-o", str(output_dir),
                        "-m", "auto",  # Auto-detect method
                        "-b", "pipeline"  # Use pipeline backend
                    ]
                    
                    logger.info(f"Running MinerU v2: {' '.join(cmd)}")
                    
                    # Run with timeout (synchronous for now since we're not in async context)
                    result = await asyncio.to_thread(
                        subprocess.run,
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=60  # 1 minute timeout should be enough
                    )
                    
                    if result.returncode != 0:
                        error_msg = result.stderr if result.stderr else "Unknown error"
                        raise RuntimeError(f"MinerU failed with code {result.returncode}: {error_msg[:500]}")
                    
                    # Find the generated markdown file
                    # MinerU v2 creates: output_dir/pdf_name/auto/pdf_name.md
                    pdf_name_no_ext = file_path.stem
                    expected_md = output_dir / pdf_name_no_ext / "auto" / f"{pdf_name_no_ext}.md"
                    
                    # Check the expected location first
                    if expected_md.exists():
                        md_content = expected_md.read_text(encoding='utf-8', errors='ignore')
                    else:
                        # Fallback to searching for any markdown file
                        md_files = list(output_dir.glob("**/*.md"))
                        if not md_files:
                            # List all files for debugging
                            all_files = list(output_dir.rglob("*"))
                            logger.warning(f"MinerU output files: {[str(f.relative_to(output_dir)) for f in all_files if f.is_file()]}")
                            raise ValueError("MinerU did not generate markdown output")
                        else:
                            # Use the first markdown file found
                            md_content = md_files[0].read_text(encoding='utf-8', errors='ignore')
                            logger.info(f"Found markdown at: {md_files[0].relative_to(output_dir)}")
                    
                    # Save to target location
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    output_path.write_text(md_content, encoding='utf-8')
                    
                    logger.info(f"Successfully converted {file_path.name} to Markdown using MinerU v2")
                    return True
                    
            except subprocess.TimeoutExpired:
                logger.error(f"MinerU conversion TIMED OUT for {file_path}")
                print(f"ERROR: MinerU timed out for {file_path.name}")
            except Exception as e:
                logger.error(f"MinerU conversion FAILED for {file_path}: {e}")
                print(f"ERROR: MinerU failed for {file_path.name}: {e}")
        
        # Try MarkItDown as alternative (not a silent fallback)
        try:
            markitdown = self._get_markitdown()
            
            # Convert to markdown
            result = await asyncio.to_thread(
                markitdown.convert,
                str(file_path)
            )
            
            # Save the markdown content
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(result.text_content)
            
            logger.info(f"Successfully converted {file_path.name} to Markdown using MarkItDown (MinerU was unavailable or failed)")
            return True
            
        except Exception as e:
            logger.error(f"MarkItDown also FAILED to convert PDF {file_path}: {e}")
            print(f"ERROR: Both MinerU and MarkItDown failed for {file_path.name}")
            # FAIL LOUDLY
            raise RuntimeError(f"PDF conversion completely failed: {e}")
    
    async def process_upload(self, file_path: Path, experiment_id: str) -> Dict:
        """Process an uploaded file, converting if necessary.
        
        Args:
            file_path: Path to the uploaded file
            experiment_id: ID of the experiment
            
        Returns:
            Dictionary with conversion results
        """
        result = {
            "filename": file_path.name,
            "original_path": str(file_path.relative_to(self.project_root)),
            "converted_path": None,
            "conversion_status": "not_needed",
            "conversion_method": None,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check if conversion is needed
        if not self.needs_conversion(file_path.name):
            logger.info(f"No conversion needed for {file_path.name}")
            # Add to registry even if no conversion needed
            await self.update_registry(experiment_id, result)
            return result
        
        # FAIL EARLY if no experiment_id
        if not experiment_id:
            error_msg = f"No experiment_id provided for file conversion"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        # Converted files go to the experiment folder root (visible to user)
        # Original PDFs are in originals/, converted .md goes to experiment root
        exp_dir = self.project_root / experiment_id
        md_filename = f"{file_path.stem}.md"
        converted_path = exp_dir / md_filename
        
        # Determine file type and convert
        ext = file_path.suffix.lower()
        conversion_success = False
        
        if ext == '.pdf':
            conversion_success = await self.convert_pdf_to_markdown(file_path, converted_path)
            result["conversion_method"] = "MinerU" if self._mineru_available else "MarkItDown"
        elif ext in ['.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls', '.html', '.htm', '.rtf', '.odt', '.odp', '.ods']:
            conversion_success = await self.convert_office_to_markdown(file_path, converted_path)
            result["conversion_method"] = "MarkItDown"
        else:
            logger.warning(f"Unsupported file type for conversion: {ext}")
            result["conversion_status"] = "unsupported"
            await self.update_registry(experiment_id, result)
            return result
        
        # Update result based on conversion outcome
        if conversion_success:
            # Verify the file was actually created
            if converted_path.exists():
                result["converted_path"] = str(converted_path.relative_to(self.project_root))
                result["conversion_status"] = "success"
                logger.info(f"Successfully created converted file: {converted_path}")
            else:
                result["conversion_status"] = "failed"
                logger.error(f"Conversion claimed success but file not created: {converted_path}")
        else:
            result["conversion_status"] = "failed"
            logger.error(f"Conversion failed for {file_path.name}")
        
        # Always update registry regardless of conversion outcome
        await self.update_registry(experiment_id, result)
        
        return result
    
    async def update_registry(self, experiment_id: str, file_info: Dict):
        """Update the file registry with conversion information.
        
        Args:
            experiment_id: ID of the experiment
            file_info: File information including conversion details
        """
        exp_dir = self.project_root / experiment_id
        registry_path = exp_dir / ".labacc" / "file_registry.json"
        
        # Load existing registry or create new
        if registry_path.exists():
            with open(registry_path, 'r') as f:
                registry = json.load(f)
        else:
            registry = {
                "version": "3.0",
                "experiment_id": experiment_id,
                "files": {},
                "last_updated": None
            }
            registry_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Update registry with new file info
        filename = file_info["filename"]
        registry["files"][filename] = {
            "original_path": file_info["original_path"],
            "converted_path": file_info.get("converted_path"),
            "upload_time": file_info["timestamp"],
            "conversion": {
                "status": file_info["conversion_status"],
                "method": file_info.get("conversion_method"),
                "timestamp": file_info["timestamp"] if file_info["conversion_status"] == "success" else None
            }
        }
        registry["last_updated"] = datetime.now().isoformat()
        
        # Save registry
        with open(registry_path, 'w') as f:
            json.dump(registry, f, indent=2)
        
        logger.info(f"Updated file registry for {experiment_id}/{filename}")
    
    async def get_file_info(self, experiment_id: str, filename: str) -> Optional[Dict]:
        """Get file information from registry.
        
        Args:
            experiment_id: ID of the experiment
            filename: Name of the file
            
        Returns:
            File information from registry, or None if not found
        """
        exp_dir = self.project_root / experiment_id
        registry_path = exp_dir / ".labacc" / "file_registry.json"
        
        if not registry_path.exists():
            return None
        
        with open(registry_path, 'r') as f:
            registry = json.load(f)
        
        return registry.get("files", {}).get(filename)
    
    async def notify_agent_for_analysis(self, experiment_id: str, filename: str):
        """Notify the agent that a new file has been uploaded and converted.
        
        This is a placeholder for WebSocket notification or similar mechanism.
        
        Args:
            experiment_id: ID of the experiment
            filename: Name of the uploaded file
        """
        # TODO: Implement WebSocket notification to trigger agent analysis
        logger.info(f"Agent notification: New file {filename} ready for analysis in {experiment_id}")


# Convenience functions for backward compatibility
async def convert_office_to_markdown_internal(
    file_path: str,
    output_path: str,
    project_root: str = "data/alice_projects"
) -> bool:
    """Internal function for Office → Markdown conversion.
    
    Args:
        file_path: Path to Office document
        output_path: Where to save Markdown
        project_root: Project root directory
        
    Returns:
        True if successful, False otherwise
    """
    pipeline = FileConversionPipeline(project_root)
    return await pipeline.convert_office_to_markdown(Path(file_path), Path(output_path))


async def convert_pdf_to_markdown_internal(
    file_path: str,
    output_path: str,
    project_root: str = "data/alice_projects"
) -> bool:
    """Internal function for PDF → Markdown conversion.
    
    Args:
        file_path: Path to PDF
        output_path: Where to save Markdown
        project_root: Project root directory
        
    Returns:
        True if successful, False otherwise
    """
    pipeline = FileConversionPipeline(project_root)
    return await pipeline.convert_pdf_to_markdown(Path(file_path), Path(output_path))