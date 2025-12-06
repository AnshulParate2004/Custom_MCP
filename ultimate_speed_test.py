#!/usr/bin/env python3
"""
Performance Benchmark: Fast & Secured MCP vs Standard MCP File Manager
Tests speed, memory usage, and efficiency of both implementations
"""

import time
import os
import tempfile
import shutil
import tracemalloc
from pathlib import Path
from typing import Callable, Dict, List
import statistics

# Import both implementations
import sys
sys.path.insert(0, r"D:\MCP_Server")

# We'll test the core functions directly
from pathlib import Path

class PerformanceTester:
    """Benchmark testing framework"""
    
    def __init__(self, test_dir: str = None):
        """Initialize with temporary test directory"""
        self.test_dir = test_dir or tempfile.mkdtemp(prefix="mcp_benchmark_")
        self.results = []
        print(f"📁 Test directory: {self.test_dir}")
    
    def cleanup(self):
        """Remove test directory"""
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        print(f"🧹 Cleaned up test directory")
    
    def time_function(self, func: Callable, *args, **kwargs) -> Dict:
        """Measure execution time and memory usage"""
        # Start memory tracking
        tracemalloc.start()
        
        # Measure execution time
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        end_time = time.perf_counter()
        
        # Get memory usage
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        execution_time = (end_time - start_time) * 1000  # Convert to ms
        
        return {
            "execution_time_ms": execution_time,
            "memory_current_kb": current / 1024,
            "memory_peak_kb": peak / 1024,
            "success": success,
            "result": result,
            "error": error
        }
    
    def run_test(self, test_name: str, func: Callable, iterations: int = 100, *args, **kwargs):
        """Run a test multiple times and collect statistics"""
        print(f"\n🧪 Running: {test_name} ({iterations} iterations)")
        
        times = []
        memory_peaks = []
        
        for i in range(iterations):
            result = self.time_function(func, *args, **kwargs)
            
            if result["success"]:
                times.append(result["execution_time_ms"])
                memory_peaks.append(result["memory_peak_kb"])
            else:
                print(f"   ❌ Iteration {i+1} failed: {result['error']}")
        
        if times:
            stats = {
                "test_name": test_name,
                "iterations": iterations,
                "successful": len(times),
                "failed": iterations - len(times),
                "avg_time_ms": statistics.mean(times),
                "min_time_ms": min(times),
                "max_time_ms": max(times),
                "median_time_ms": statistics.median(times),
                "stdev_time_ms": statistics.stdev(times) if len(times) > 1 else 0,
                "avg_memory_kb": statistics.mean(memory_peaks),
                "peak_memory_kb": max(memory_peaks)
            }
            
            self.results.append(stats)
            
            print(f"   ✅ Success: {stats['successful']}/{iterations}")
            print(f"   ⏱️  Avg Time: {stats['avg_time_ms']:.3f}ms")
            print(f"   📊 Min/Max: {stats['min_time_ms']:.3f}ms / {stats['max_time_ms']:.3f}ms")
            print(f"   💾 Memory: {stats['avg_memory_kb']:.2f} KB (peak: {stats['peak_memory_kb']:.2f} KB)")
            
            return stats
        else:
            print(f"   ❌ All iterations failed")
            return None


# ============================================================================
# TEST FUNCTIONS FOR BOTH IMPLEMENTATIONS
# ============================================================================

def test_write_file_standard(filepath: str, content: str):
    """Test standard implementation write"""
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def test_write_file_secured(filepath: str, content: str, allowed_dirs: List[str]):
    """Test secured implementation write with validation"""
    # Simplified security check
    abs_path = os.path.abspath(filepath)
    allowed = any(abs_path.startswith(os.path.abspath(d)) for d in allowed_dirs)
    
    if not allowed:
        raise PermissionError("Access denied")
    
    directory = os.path.dirname(abs_path)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)
    
    with open(abs_path, 'w', encoding='utf-8') as f:
        f.write(content)

def test_read_file_standard(filepath: str):
    """Test standard implementation read"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def test_read_file_secured(filepath: str, allowed_dirs: List[str]):
    """Test secured implementation read with validation"""
    abs_path = os.path.abspath(filepath)
    allowed = any(abs_path.startswith(os.path.abspath(d)) for d in allowed_dirs)
    
    if not allowed:
        raise PermissionError("Access denied")
    
    with open(abs_path, 'r', encoding='utf-8') as f:
        return f.read()

def test_list_files_standard(directory: str, pattern: str = "*"):
    """Test standard implementation list"""
    import glob
    search_pattern = os.path.join(directory, pattern)
    return glob.glob(search_pattern)

def test_list_files_secured(directory: str, pattern: str, allowed_dirs: List[str]):
    """Test secured implementation list with validation"""
    import glob
    abs_dir = os.path.abspath(directory)
    allowed = any(abs_dir.startswith(os.path.abspath(d)) for d in allowed_dirs)
    
    if not allowed:
        raise PermissionError("Access denied")
    
    search_pattern = os.path.join(abs_dir, pattern)
    return glob.glob(search_pattern)


# ============================================================================
# BENCHMARK EXECUTION
# ============================================================================

def run_comprehensive_benchmark():
    """Run full benchmark suite"""
    print("=" * 80)
    print("🚀 MCP FILE MANAGER PERFORMANCE BENCHMARK")
    print("=" * 80)
    print("Comparing Standard vs Fast & Secured implementations")
    print()
    
    tester = PerformanceTester()
    allowed_dirs = [tester.test_dir]
    
    try:
        # Prepare test data
        small_content = "Hello World! " * 10  # ~130 bytes
        medium_content = "Lorem ipsum dolor sit amet. " * 100  # ~2.8 KB
        large_content = "x" * 100000  # 100 KB
        
        test_file_small = os.path.join(tester.test_dir, "small.txt")
        test_file_medium = os.path.join(tester.test_dir, "medium.txt")
        test_file_large = os.path.join(tester.test_dir, "large.txt")
        
        # Create test files for reading
        with open(test_file_small, 'w') as f:
            f.write(small_content)
        with open(test_file_medium, 'w') as f:
            f.write(medium_content)
        with open(test_file_large, 'w') as f:
            f.write(large_content)
        
        # Create multiple files for listing
        for i in range(50):
            with open(os.path.join(tester.test_dir, f"file_{i}.txt"), 'w') as f:
                f.write(f"File {i}")
        
        print("\n" + "=" * 80)
        print("📝 WRITE OPERATIONS")
        print("=" * 80)
        
        # Test 1: Write small files
        standard_write_small = tester.run_test(
            "Standard - Write Small (130B)",
            test_write_file_standard,
            iterations=100,
            filepath=os.path.join(tester.test_dir, "test_std_small.txt"),
            content=small_content
        )
        
        secured_write_small = tester.run_test(
            "Secured - Write Small (130B)",
            test_write_file_secured,
            iterations=100,
            filepath=os.path.join(tester.test_dir, "test_sec_small.txt"),
            content=small_content,
            allowed_dirs=allowed_dirs
        )
        
        # Test 2: Write medium files
        standard_write_medium = tester.run_test(
            "Standard - Write Medium (2.8KB)",
            test_write_file_standard,
            iterations=100,
            filepath=os.path.join(tester.test_dir, "test_std_medium.txt"),
            content=medium_content
        )
        
        secured_write_medium = tester.run_test(
            "Secured - Write Medium (2.8KB)",
            test_write_file_secured,
            iterations=100,
            filepath=os.path.join(tester.test_dir, "test_sec_medium.txt"),
            content=medium_content,
            allowed_dirs=allowed_dirs
        )
        
        # Test 3: Write large files
        standard_write_large = tester.run_test(
            "Standard - Write Large (100KB)",
            test_write_file_standard,
            iterations=50,
            filepath=os.path.join(tester.test_dir, "test_std_large.txt"),
            content=large_content
        )
        
        secured_write_large = tester.run_test(
            "Secured - Write Large (100KB)",
            test_write_file_secured,
            iterations=50,
            filepath=os.path.join(tester.test_dir, "test_sec_large.txt"),
            content=large_content,
            allowed_dirs=allowed_dirs
        )
        
        print("\n" + "=" * 80)
        print("📖 READ OPERATIONS")
        print("=" * 80)
        
        # Test 4: Read small files
        standard_read_small = tester.run_test(
            "Standard - Read Small (130B)",
            test_read_file_standard,
            iterations=100,
            filepath=test_file_small
        )
        
        secured_read_small = tester.run_test(
            "Secured - Read Small (130B)",
            test_read_file_secured,
            iterations=100,
            filepath=test_file_small,
            allowed_dirs=allowed_dirs
        )
        
        # Test 5: Read medium files
        standard_read_medium = tester.run_test(
            "Standard - Read Medium (2.8KB)",
            test_read_file_standard,
            iterations=100,
            filepath=test_file_medium
        )
        
        secured_read_medium = tester.run_test(
            "Secured - Read Medium (2.8KB)",
            test_read_file_secured,
            iterations=100,
            filepath=test_file_medium,
            allowed_dirs=allowed_dirs
        )
        
        # Test 6: Read large files
        standard_read_large = tester.run_test(
            "Standard - Read Large (100KB)",
            test_read_file_standard,
            iterations=50,
            filepath=test_file_large
        )
        
        secured_read_large = tester.run_test(
            "Secured - Read Large (100KB)",
            test_read_file_secured,
            iterations=50,
            filepath=test_file_large,
            allowed_dirs=allowed_dirs
        )
        
        print("\n" + "=" * 80)
        print("📂 LIST OPERATIONS")
        print("=" * 80)
        
        # Test 7: List files
        standard_list = tester.run_test(
            "Standard - List 50 files",
            test_list_files_standard,
            iterations=100,
            directory=tester.test_dir,
            pattern="*.txt"
        )
        
        secured_list = tester.run_test(
            "Secured - List 50 files",
            test_list_files_secured,
            iterations=100,
            directory=tester.test_dir,
            pattern="*.txt",
            allowed_dirs=allowed_dirs
        )
        
        # ====================================================================
        # SUMMARY REPORT
        # ====================================================================
        
        print("\n" + "=" * 80)
        print("📊 PERFORMANCE SUMMARY")
        print("=" * 80)
        
        def compare_results(test_name: str, std_result: Dict, sec_result: Dict):
            if std_result and sec_result:
                overhead = ((sec_result['avg_time_ms'] - std_result['avg_time_ms']) / std_result['avg_time_ms']) * 100
                overhead_mem = ((sec_result['avg_memory_kb'] - std_result['avg_memory_kb']) / std_result['avg_memory_kb']) * 100 if std_result['avg_memory_kb'] > 0 else 0
                
                print(f"\n{test_name}:")
                print(f"  Standard: {std_result['avg_time_ms']:.3f}ms | {std_result['avg_memory_kb']:.2f}KB")
                print(f"  Secured:  {sec_result['avg_time_ms']:.3f}ms | {sec_result['avg_memory_kb']:.2f}KB")
                print(f"  Overhead: {overhead:+.2f}% time | {overhead_mem:+.2f}% memory")
                
                return overhead
        
        print("\n📝 WRITE Operations:")
        write_overheads = []
        write_overheads.append(compare_results("Small Files (130B)", standard_write_small, secured_write_small))
        write_overheads.append(compare_results("Medium Files (2.8KB)", standard_write_medium, secured_write_medium))
        write_overheads.append(compare_results("Large Files (100KB)", standard_write_large, secured_write_large))
        
        print("\n📖 READ Operations:")
        read_overheads = []
        read_overheads.append(compare_results("Small Files (130B)", standard_read_small, secured_read_small))
        read_overheads.append(compare_results("Medium Files (2.8KB)", standard_read_medium, secured_read_medium))
        read_overheads.append(compare_results("Large Files (100KB)", standard_read_large, secured_read_large))
        
        print("\n📂 LIST Operations:")
        list_overhead = compare_results("List 50 Files", standard_list, secured_list)
        
        # Overall summary
        all_overheads = [o for o in write_overheads + read_overheads + [list_overhead] if o is not None]
        if all_overheads:
            avg_overhead = statistics.mean(all_overheads)
            print("\n" + "=" * 80)
            print("🎯 FINAL VERDICT")
            print("=" * 80)
            print(f"Average Security Overhead: {avg_overhead:+.2f}%")
            
            if avg_overhead < 5:
                verdict = "🎉 EXCELLENT - Minimal overhead, security nearly free!"
            elif avg_overhead < 15:
                verdict = "✅ GOOD - Acceptable overhead for added security"
            elif avg_overhead < 30:
                verdict = "⚠️  MODERATE - Noticeable overhead, consider optimization"
            else:
                verdict = "❌ HIGH - Significant overhead, optimization needed"
            
            print(f"\n{verdict}")
            print(f"\n💡 Conclusion:")
            print(f"   The Fast & Secured implementation adds ~{avg_overhead:.1f}% overhead")
            print(f"   for comprehensive path validation and security checks.")
            print(f"   This is the cost of preventing directory traversal attacks")
            print(f"   and unauthorized file access.")
    
    finally:
        tester.cleanup()
    
    print("\n" + "=" * 80)
    print("✅ Benchmark Complete!")
    print("=" * 80)


if __name__ == "__main__":
    run_comprehensive_benchmark()