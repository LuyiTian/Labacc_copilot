"""Quick file analysis for LabAcc Copilot"""

import os
import pandas as pd
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, List, Any
from langchain_core.messages import HumanMessage
from langchain_core.language_models import BaseLLM


@dataclass
class FileAnalysis:
    """Analysis results for a single file"""
    file_path: str
    file_name: str
    file_type: str              # "csv", "image", "text", etc.
    size_bytes: int
    content_summary: str        # AI-generated summary
    data_points: Optional[int]  # For CSV files
    image_metadata: Optional[Dict]  # For images
    analysis_confidence: float
    error_message: Optional[str] = None


class QuickFileAnalyzer:
    """Provide quick analysis of uploaded experimental files"""
    
    def __init__(self, llm: BaseLLM):
        self.llm = llm
        
        # File type detection
        self.csv_extensions = {'.csv', '.tsv', '.txt'}
        self.excel_extensions = {'.xlsx', '.xls'}
        self.image_extensions = {'.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.gif'}
        self.text_extensions = {'.txt', '.md', '.log', '.json', '.yaml', '.yml'}
        
    def detect_file_type(self, file_path: str) -> str:
        """Detect file type based on extension"""
        ext = Path(file_path).suffix.lower()
        
        if ext in self.csv_extensions:
            return "csv"
        elif ext in self.excel_extensions:
            return "excel"
        elif ext in self.image_extensions:
            return "image"
        elif ext in self.text_extensions:
            return "text"
        else:
            return "unknown"
    
    async def analyze_file(self, file_path: str) -> FileAnalysis:
        """Quick analysis of uploaded file"""
        file_name = os.path.basename(file_path)
        file_type = self.detect_file_type(file_path)
        size_bytes = os.path.getsize(file_path) if os.path.exists(file_path) else 0
        
        try:
            if file_type == "csv":
                return await self._analyze_csv(file_path, file_name, size_bytes)
            elif file_type == "excel":
                return await self._analyze_excel(file_path, file_name, size_bytes)
            elif file_type == "image":
                return await self._analyze_image(file_path, file_name, size_bytes)
            elif file_type == "text":
                return await self._analyze_text(file_path, file_name, size_bytes)
            else:
                return await self._analyze_generic(file_path, file_name, file_type, size_bytes)
                
        except Exception as e:
            return FileAnalysis(
                file_path=file_path,
                file_name=file_name,
                file_type=file_type,
                size_bytes=size_bytes,
                content_summary=f"Error analyzing file: {str(e)}",
                data_points=None,
                image_metadata=None,
                analysis_confidence=0.0,
                error_message=str(e)
            )
    
    async def _analyze_csv(self, file_path: str, file_name: str, size_bytes: int) -> FileAnalysis:
        """Analyze CSV/TSV data files"""
        try:
            # Read with pandas, limit to first 1000 rows for quick analysis
            df = pd.read_csv(file_path, nrows=1000)
            
            rows, cols = df.shape
            data_points = rows * cols
            
            # Generate summary
            summary_parts = [
                f"CSV file with {rows} rows and {cols} columns",
                f"Columns: {', '.join(df.columns.tolist()[:5])}" + ("..." if len(df.columns) > 5 else "")
            ]
            
            # Check for numeric data
            numeric_cols = df.select_dtypes(include=['number']).columns.tolist()
            if numeric_cols:
                summary_parts.append(f"Numeric columns: {', '.join(numeric_cols[:3])}" + ("..." if len(numeric_cols) > 3 else ""))
                
                # Basic statistics for first numeric column
                first_numeric = numeric_cols[0]
                stats = df[first_numeric].describe()
                summary_parts.append(f"{first_numeric}: mean={stats['mean']:.2f}, range={stats['min']:.2f}-{stats['max']:.2f}")
            
            content_summary = ". ".join(summary_parts)
            
            return FileAnalysis(
                file_path=file_path,
                file_name=file_name,
                file_type="csv",
                size_bytes=size_bytes,
                content_summary=content_summary,
                data_points=data_points,
                image_metadata=None,
                analysis_confidence=0.9
            )
            
        except Exception as e:
            return FileAnalysis(
                file_path=file_path,
                file_name=file_name,
                file_type="csv",
                size_bytes=size_bytes,
                content_summary=f"CSV file (unable to parse: {str(e)})",
                data_points=None,
                image_metadata=None,
                analysis_confidence=0.1,
                error_message=str(e)
            )
    
    async def _analyze_excel(self, file_path: str, file_name: str, size_bytes: int) -> FileAnalysis:
        """Analyze Excel files"""
        try:
            # Read first sheet with pandas
            df = pd.read_excel(file_path, nrows=1000)
            
            rows, cols = df.shape
            data_points = rows * cols
            
            summary = f"Excel file with {rows} rows and {cols} columns. Columns: {', '.join(df.columns.tolist()[:5])}"
            if len(df.columns) > 5:
                summary += "..."
            
            return FileAnalysis(
                file_path=file_path,
                file_name=file_name,
                file_type="excel",
                size_bytes=size_bytes,
                content_summary=summary,
                data_points=data_points,
                image_metadata=None,
                analysis_confidence=0.8
            )
            
        except Exception as e:
            return FileAnalysis(
                file_path=file_path,
                file_name=file_name,
                file_type="excel",
                size_bytes=size_bytes,
                content_summary=f"Excel file (unable to parse: {str(e)})",
                data_points=None,
                image_metadata=None,
                analysis_confidence=0.1,
                error_message=str(e)
            )
    
    async def _analyze_image(self, file_path: str, file_name: str, size_bytes: int) -> FileAnalysis:
        """Analyze image files"""
        try:
            from PIL import Image
            
            with Image.open(file_path) as img:
                width, height = img.size
                format_info = img.format
                mode = img.mode
                
                image_metadata = {
                    "width": width,
                    "height": height,
                    "format": format_info,
                    "mode": mode,
                    "megapixels": round((width * height) / 1000000, 2)
                }
                
                summary = f"{format_info} image, {width}×{height} pixels, {image_metadata['megapixels']}MP, {mode} mode"
                
                # Use LLM for content analysis if available
                if hasattr(self.llm, 'multimodal') or 'vision' in str(type(self.llm)).lower():
                    try:
                        content_analysis = await self._analyze_image_content(file_path)
                        if content_analysis:
                            summary += f". Content: {content_analysis}"
                    except:
                        pass  # Fallback to basic metadata
                
                return FileAnalysis(
                    file_path=file_path,
                    file_name=file_name,
                    file_type="image",
                    size_bytes=size_bytes,
                    content_summary=summary,
                    data_points=width * height,
                    image_metadata=image_metadata,
                    analysis_confidence=0.8
                )
                
        except Exception as e:
            return FileAnalysis(
                file_path=file_path,
                file_name=file_name,
                file_type="image",
                size_bytes=size_bytes,
                content_summary=f"Image file (unable to analyze: {str(e)})",
                data_points=None,
                image_metadata=None,
                analysis_confidence=0.1,
                error_message=str(e)
            )
    
    async def _analyze_image_content(self, file_path: str) -> str:
        """Analyze image content using vision LLM"""
        try:
            # This would be implemented for vision-capable LLMs
            # For now, return placeholder
            return "Laboratory image detected"
        except:
            return ""
    
    async def _analyze_text(self, file_path: str, file_name: str, size_bytes: int) -> FileAnalysis:
        """Analyze text files"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read(1000)  # First 1000 characters
            
            lines = content.count('\n') + 1
            words = len(content.split())
            
            # Use LLM for content summary
            summary_prompt = f"""Briefly analyze this text file content (first 1000 characters):

Filename: {file_name}
Content preview:
{content}

Provide a 1-2 sentence summary of what this file contains."""
            
            try:
                response = await self.llm.ainvoke([HumanMessage(content=summary_prompt)])
                content_summary = response.content.strip()
                confidence = 0.8
            except:
                content_summary = f"Text file with {lines} lines and {words} words"
                confidence = 0.5
            
            return FileAnalysis(
                file_path=file_path,
                file_name=file_name,
                file_type="text",
                size_bytes=size_bytes,
                content_summary=content_summary,
                data_points=words,
                image_metadata=None,
                analysis_confidence=confidence
            )
            
        except Exception as e:
            return FileAnalysis(
                file_path=file_path,
                file_name=file_name,
                file_type="text",
                size_bytes=size_bytes,
                content_summary=f"Text file (unable to read: {str(e)})",
                data_points=None,
                image_metadata=None,
                analysis_confidence=0.1,
                error_message=str(e)
            )
    
    async def _analyze_generic(self, file_path: str, file_name: str, file_type: str, size_bytes: int) -> FileAnalysis:
        """Analyze unknown file types"""
        return FileAnalysis(
            file_path=file_path,
            file_name=file_name,
            file_type=file_type,
            size_bytes=size_bytes,
            content_summary=f"File of type {file_type}, {self._format_size(size_bytes)}",
            data_points=None,
            image_metadata=None,
            analysis_confidence=0.3
        )
    
    def _format_size(self, size_bytes: int) -> str:
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f}{unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f}TB"
    
    async def analyze_multiple_files(self, file_paths: List[str]) -> List[FileAnalysis]:
        """Analyze multiple files and return results"""
        analyses = []
        for file_path in file_paths:
            analysis = await self.analyze_file(file_path)
            analyses.append(analysis)
        return analyses
    
    def generate_summary_report(self, analyses: List[FileAnalysis]) -> str:
        """Generate summary report for multiple file analyses"""
        if not analyses:
            return "No files analyzed."
        
        total_files = len(analyses)
        total_size = sum(a.size_bytes for a in analyses)
        
        # Group by file type
        type_counts = {}
        for analysis in analyses:
            type_counts[analysis.file_type] = type_counts.get(analysis.file_type, 0) + 1
        
        report_parts = [
            f"📊 **Analysis Summary**: {total_files} files, {self._format_size(total_size)} total"
        ]
        
        # File type breakdown
        if len(type_counts) > 1:
            type_breakdown = ", ".join([f"{count} {ftype}" for ftype, count in type_counts.items()])
            report_parts.append(f"**File types**: {type_breakdown}")
        
        # Individual file summaries
        report_parts.append("**Files analyzed**:")
        for analysis in analyses:
            icon = self._get_file_icon(analysis.file_type)
            report_parts.append(f"- {icon} **{analysis.file_name}**: {analysis.content_summary}")
        
        return "\n".join(report_parts)
    
    def _get_file_icon(self, file_type: str) -> str:
        """Get appropriate icon for file type"""
        icons = {
            "csv": "📊",
            "excel": "📊", 
            "image": "🖼️",
            "text": "📄",
            "unknown": "📄"
        }
        return icons.get(file_type, "📄")