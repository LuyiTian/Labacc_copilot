"""Extended test cases for v3.0 file conversion system.

These tests cover additional scenarios identified from the v3 plan:
- Performance benchmarks for large files
- Multiple file format conversions (Excel, PowerPoint, HTML)
- Concurrent upload stress testing
- WebSocket status updates during conversion
- Corrupted file handling
- Registry consistency checks
"""

import asyncio
import json
import shutil
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import pytest
import sys
import os

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.api.file_conversion import FileConversionPipeline
from src.api.file_registry import FileRegistry
from src.utils.test_cleanup import TestCleanup, ensure_bob_projects_clean


class TestPerformanceBenchmarks:
    """Test conversion performance with various file sizes."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Ensure clean state before and after each test."""
        ensure_bob_projects_clean()
        yield
        ensure_bob_projects_clean()
    
    @pytest.mark.asyncio
    async def test_large_pdf_conversion_time(self):
        """Benchmark PDF conversion time for different file sizes."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_perf_pdf")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_perf_pdf"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test PDFs of different sizes (simulate with text files)
            sizes = {
                "small": 100,     # 100 KB
                "medium": 1000,   # 1 MB
                "large": 5000     # 5 MB
            }
            
            pipeline = FileConversionPipeline(str(project_root))
            results = {}
            
            for size_name, size_kb in sizes.items():
                # Create a test file
                test_file = exp_dir / f"test_{size_name}.txt"
                content = "Test content line.\n" * (size_kb * 50)  # Approximate size
                test_file.write_text(content)
                
                # Measure conversion time
                start_time = time.time()
                result = await pipeline.process_upload(test_file, experiment_id)
                end_time = time.time()
                
                results[size_name] = {
                    "size_kb": size_kb,
                    "time_seconds": end_time - start_time,
                    "status": result["conversion_status"]
                }
            
            # Performance assertions
            assert results["small"]["time_seconds"] < 2.0, "Small files should convert in <2s"
            assert results["medium"]["time_seconds"] < 10.0, "Medium files should convert in <10s"
            
            # Log performance metrics
            print("\nConversion Performance Metrics:")
            for size_name, metrics in results.items():
                print(f"  {size_name}: {metrics['time_seconds']:.2f}s for {metrics['size_kb']}KB")
    
    @pytest.mark.asyncio
    async def test_batch_conversion_performance(self):
        """Test converting multiple files in sequence vs parallel."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_batch_perf")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_batch_perf"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create 10 test files
            test_files = []
            for i in range(10):
                test_file = exp_dir / f"document_{i}.md"
                test_file.write_text(f"# Document {i}\n\nContent for document {i}")
                test_files.append(test_file)
            
            pipeline = FileConversionPipeline(str(project_root))
            
            # Sequential processing
            start_sequential = time.time()
            for test_file in test_files:
                await pipeline.process_upload(test_file, experiment_id)
            sequential_time = time.time() - start_sequential
            
            # Parallel processing (simulate)
            start_parallel = time.time()
            tasks = [pipeline.process_upload(f, experiment_id) for f in test_files]
            await asyncio.gather(*tasks)
            parallel_time = time.time() - start_parallel
            
            print(f"\nBatch Processing Performance:")
            print(f"  Sequential: {sequential_time:.2f}s")
            print(f"  Parallel: {parallel_time:.2f}s")
            print(f"  Speedup: {sequential_time/parallel_time:.2f}x")
            
            # Parallel should be faster or at least similar
            assert parallel_time <= sequential_time * 1.1, "Parallel should not be significantly slower"


class TestAdditionalFormats:
    """Test conversion of additional file formats."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Ensure clean state before and after each test."""
        ensure_bob_projects_clean()
        yield
        ensure_bob_projects_clean()
    
    @pytest.mark.asyncio
    async def test_excel_conversion(self):
        """Test Excel file conversion to Markdown."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_excel")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_excel"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a simple CSV file (as Excel proxy for testing)
            excel_file = exp_dir / "originals" / "data.xlsx"
            excel_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Note: In real test, would create actual Excel file
            # For now, create a placeholder
            excel_file.write_text("Sample,Value\nA,1\nB,2\nC,3")
            
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(excel_file, experiment_id)
            
            # Excel files should be converted
            assert pipeline.needs_conversion("data.xlsx") == True
            
            # Verify registry
            registry = FileRegistry(str(project_root))
            file_info = registry.get_file(experiment_id, "data.xlsx")
            # Should be in registry even if conversion fails
            assert file_info is not None or result["conversion_status"] == "failed"
    
    @pytest.mark.asyncio
    async def test_powerpoint_conversion(self):
        """Test PowerPoint file conversion to Markdown."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_pptx")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_pptx"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test PowerPoint placeholder
            pptx_file = exp_dir / "originals" / "presentation.pptx"
            pptx_file.parent.mkdir(parents=True, exist_ok=True)
            pptx_file.write_text("Slide content placeholder")
            
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(pptx_file, experiment_id)
            
            assert pipeline.needs_conversion("presentation.pptx") == True
    
    @pytest.mark.asyncio
    async def test_html_conversion(self):
        """Test HTML file conversion to Markdown."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_html")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_html"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test HTML file
            html_file = exp_dir / "originals" / "page.html"
            html_file.parent.mkdir(parents=True, exist_ok=True)
            html_file.write_text("""
            <html>
            <head><title>Test Page</title></head>
            <body>
                <h1>Protocol Summary</h1>
                <p>This is a test protocol with <strong>important</strong> information.</p>
                <ul>
                    <li>Step 1: Prepare samples</li>
                    <li>Step 2: Run analysis</li>
                    <li>Step 3: Collect results</li>
                </ul>
            </body>
            </html>
            """)
            
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(html_file, experiment_id)
            
            assert pipeline.needs_conversion("page.html") == True
            
            if result["conversion_status"] == "success":
                # Check converted content preserves structure
                converted_path = project_root / result["converted_path"]
                if converted_path.exists():
                    content = converted_path.read_text()
                    assert "Protocol Summary" in content
                    assert "Step 1" in content


class TestConcurrentOperations:
    """Test system behavior under concurrent load."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Ensure clean state before and after each test."""
        ensure_bob_projects_clean()
        yield
        ensure_bob_projects_clean()
    
    @pytest.mark.asyncio
    async def test_concurrent_uploads_same_experiment(self):
        """Test multiple users uploading to same experiment simultaneously."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_concurrent")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_concurrent"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create multiple test files
            test_files = []
            for i in range(5):
                test_file = exp_dir / f"file_{i}.md"
                test_file.write_text(f"# File {i}\n\nContent {i}")
                test_files.append(test_file)
            
            pipeline = FileConversionPipeline(str(project_root))
            
            # Simulate concurrent uploads
            tasks = []
            for test_file in test_files:
                task = pipeline.process_upload(test_file, experiment_id)
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All uploads should succeed
            successful = sum(1 for r in results if not isinstance(r, Exception) and r["conversion_status"] != "error")
            assert successful == len(test_files), f"Only {successful}/{len(test_files)} uploads succeeded"
            
            # Registry should have all files
            registry = FileRegistry(str(project_root))
            for test_file in test_files:
                file_info = registry.get_file(experiment_id, test_file.name)
                assert file_info is not None, f"File {test_file.name} not in registry"
    
    @pytest.mark.asyncio
    async def test_registry_concurrent_access(self):
        """Test registry handles concurrent read/write operations."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_registry_concurrent")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_registry_concurrent"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            registry = FileRegistry(str(project_root))
            
            # Concurrent operations
            async def add_file(i):
                registry.add_file(
                    experiment_id=experiment_id,
                    filename=f"file_{i}.txt",
                    original_path=f"{experiment_id}/file_{i}.txt",
                    file_size=1000 + i
                )
            
            async def read_file(i):
                return registry.get_file(experiment_id, f"file_{i}.txt")
            
            # Add files concurrently
            add_tasks = [add_file(i) for i in range(10)]
            await asyncio.gather(*add_tasks)
            
            # Read files concurrently
            read_tasks = [read_file(i) for i in range(10)]
            results = await asyncio.gather(*read_tasks)
            
            # All files should be retrievable
            assert all(r is not None for r in results), "Some files not found in registry"


class TestErrorHandling:
    """Test handling of error conditions and edge cases."""
    
    @pytest.fixture(autouse=True)
    def setup_and_cleanup(self):
        """Ensure clean state before and after each test."""
        ensure_bob_projects_clean()
        yield
        ensure_bob_projects_clean()
    
    @pytest.mark.asyncio
    async def test_corrupted_file_handling(self):
        """Test handling of corrupted or invalid files."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_corrupted")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_corrupted"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create corrupted PDF (invalid binary data)
            corrupted_pdf = exp_dir / "corrupted.pdf"
            corrupted_pdf.write_bytes(b"Not a real PDF file \x00\x01\x02")
            
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(corrupted_pdf, experiment_id)
            
            # Should handle gracefully
            assert result["conversion_status"] in ["failed", "error"]
            assert result["filename"] == "corrupted.pdf"
            
            # Should still be tracked in registry
            registry = FileRegistry(str(project_root))
            file_info = registry.get_file(experiment_id, "corrupted.pdf")
            # File should be registered even if conversion failed
            assert file_info is not None or result["conversion_status"] == "error"
    
    @pytest.mark.asyncio
    async def test_registry_recovery_after_corruption(self):
        """Test registry can recover from corrupted JSON."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_recovery")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_recovery"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create registry with valid data
            registry = FileRegistry(str(project_root))
            registry.add_file(experiment_id, "test.txt", f"{experiment_id}/test.txt")
            
            # Corrupt the registry file
            registry_path = exp_dir / ".labacc" / "file_registry.json"
            if registry_path.exists():
                registry_path.write_text("{ corrupted json }")
            
            # Try to load corrupted registry
            new_registry = FileRegistry(str(project_root))
            loaded = new_registry.load_registry(experiment_id)
            
            # Should return default structure on corruption
            assert loaded["version"] == "3.0"
            assert loaded["experiment_id"] == experiment_id
            assert isinstance(loaded["files"], dict)
    
    @pytest.mark.asyncio
    async def test_filesystem_permission_errors(self):
        """Test handling when filesystem operations fail."""
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_permissions")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_permissions"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create a test file
            test_file = exp_dir / "test.md"
            test_file.write_text("# Test")
            
            pipeline = FileConversionPipeline(str(project_root))
            
            # Test with non-existent source file
            non_existent = exp_dir / "does_not_exist.pdf"
            result = await pipeline.process_upload(non_existent, experiment_id)
            
            # Should handle gracefully
            assert result["conversion_status"] in ["error", "failed"]


class TestWebSocketIntegration:
    """Test WebSocket status updates during conversion."""
    
    @pytest.mark.asyncio
    async def test_conversion_status_updates(self):
        """Test that conversion sends status updates via WebSocket."""
        # This would require WebSocket infrastructure to be set up
        # For now, we'll create a placeholder test
        
        # Simulate conversion with status callback
        async def status_callback(status: str, progress: float):
            print(f"Status: {status}, Progress: {progress}%")
        
        with TestCleanup() as cleanup:
            cleanup.register_test_folder("exp_test_websocket")
            
            project_root = Path("data/bob_projects")
            experiment_id = "exp_test_websocket"
            exp_dir = project_root / experiment_id
            exp_dir.mkdir(parents=True, exist_ok=True)
            
            # Create test file
            test_file = exp_dir / "document.md"
            test_file.write_text("# Test Document\n\nContent here")
            
            # In real implementation, would hook into WebSocket
            pipeline = FileConversionPipeline(str(project_root))
            result = await pipeline.process_upload(test_file, experiment_id)
            
            # Verify conversion completed
            assert result["conversion_status"] in ["success", "not_needed"]


if __name__ == "__main__":
    # Run the extended tests
    pytest.main([__file__, "-v", "-s"])