import unittest
import os
import sys
import json
import tempfile
import shutil
import time
import threading
import psutil
import memory_profiler
import logging
import subprocess
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.which_password import PasswordCracker

class TestPasswordCracker(unittest.TestCase):
    def setUp(self):
        """Set up test environment before each test."""
        # Create a temporary directory for test files
        self.test_dir = tempfile.mkdtemp()
        
        # Create a test config file
        self.config_path = os.path.join(self.test_dir, "test_config.json")
        self.test_config = {
            "max_workers": 2,
            "timeout": 0,
            "output_dir": "test_extracted",
            "save_successful": True,
            "successful_passwords_file": "test_successful.txt",
            "supported_formats": [".rar", ".zip", ".7z", ".tar", ".gz"],
            "retry_limit": 100,
            "log_level": "DEBUG",
            "sevenzip_path": ""
        }
        with open(self.config_path, 'w') as f:
            json.dump(self.test_config, f)
        
        # Create a test password file
        self.password_file = os.path.join(self.test_dir, "test_passwords.txt")
        with open(self.password_file, 'w') as f:
            f.write("password1\npassword2\npassword3\n")
        
        # Create a dummy archive file for testing
        self.test_archive = os.path.join(self.test_dir, "test.rar")
        with open(self.test_archive, 'w') as f:
            f.write("dummy content")
        
        # Initialize the password cracker with test config
        self.cracker = PasswordCracker(self.config_path)

    def tearDown(self):
        """Clean up test environment after each test."""
        # Remove temporary directory and its contents
        shutil.rmtree(self.test_dir)

    def test_config_loading(self):
        """Test if configuration is loaded correctly"""
        self.assertIsNotNone(self.cracker.config)
        self.assertEqual(self.cracker.config["max_workers"], 2)
        self.assertEqual(self.cracker.config["timeout"], 0)
        self.assertEqual(self.cracker.config["output_dir"], "test_extracted")
        self.assertTrue(self.cracker.config["save_successful"])

    def test_sevenzip_path(self):
        """Test if 7-Zip path is found"""
        self.assertIsNotNone(self.cracker.sevenzip_path)
        self.assertTrue(os.path.exists(self.cracker.sevenzip_path))

    def test_invalid_config_file(self):
        """Test handling of invalid config file"""
        invalid_config_path = os.path.join(self.test_dir, "invalid_config.json")
        with open(invalid_config_path, 'w') as f:
            f.write("invalid json content")
        
        # Should use default config when invalid config is provided
        cracker = PasswordCracker(invalid_config_path)
        self.assertIsNotNone(cracker.config)
        self.assertIn("max_workers", cracker.config)

    def test_missing_password_file(self):
        """Test handling of missing password file"""
        non_existent_file = os.path.join(self.test_dir, "non_existent.txt")
        with self.assertRaises(FileNotFoundError):
            self.cracker.crack_password(self.test_archive, non_existent_file)

    def test_missing_archive_file(self):
        """Test handling of missing archive file"""
        non_existent_archive = os.path.join(self.test_dir, "non_existent.rar")
        with self.assertRaises(FileNotFoundError):
            self.cracker.crack_password(non_existent_archive, self.password_file)

    def test_save_successful_password(self):
        """Test saving successful password to file"""
        test_password = "test_password"
        self.cracker._save_successful_password(test_password)
        
        successful_file = os.path.join(self.test_dir, self.test_config["successful_passwords_file"])
        self.assertTrue(os.path.exists(successful_file))
        
        with open(successful_file, 'r') as f:
            saved_passwords = f.read().strip().split('\n')
            self.assertIn(test_password, saved_passwords)

    def test_output_directory_creation(self):
        """Test creation of output directory"""
        # Try to extract with a password
        self.cracker.try_password(self.test_archive, "test_password")
        
        # Check if output directory was created
        output_dir = os.path.join(self.test_dir, self.test_config["output_dir"])
        self.assertTrue(os.path.exists(output_dir))

    def test_unsupported_format(self):
        """Test handling of unsupported archive format"""
        test_archive = os.path.join(self.test_dir, "test.xyz")
        with open(test_archive, 'w') as f:
            f.write("dummy content")
        
        # Should still try to process but might fail with 7-Zip error
        result = self.cracker.try_password(test_archive, "test_password")
        self.assertFalse(result)

    def test_timeout_handling(self):
        """Test timeout functionality"""
        # Create a large password file to ensure the process takes time
        with open(self.password_file, 'w') as f:
            for i in range(1000):
                f.write(f"password{i}\n")

        # Set a very short timeout
        self.cracker.config["timeout"] = 0.1  # 100ms timeout

        # Create a test archive
        test_archive = os.path.join(self.test_dir, "timeout_test.7z")
        with open(test_archive, 'w') as f:
            f.write("test content")

        # Start cracking in a separate thread
        thread = threading.Thread(target=self.cracker.crack_password, args=(test_archive, self.password_file))
        thread.start()

        # Wait for the timeout
        time.sleep(0.2)  # Wait a bit longer than the timeout

        # Verify that the process has stopped
        self.assertFalse(self.cracker.running)
        thread.join(timeout=1.0)  # Wait for thread to finish
        self.assertFalse(thread.is_alive())

    def test_stop_cracking(self):
        """Test manual stopping of password cracking"""
        self.assertTrue(self.cracker.running)
        self.cracker.stop_cracking()
        self.assertFalse(self.cracker.running)

    def test_password_file_encoding(self):
        """Test handling of different password file encodings"""
        # Create a password file with UTF-8 encoding
        utf8_file = os.path.join(self.test_dir, "utf8_passwords.txt")
        with open(utf8_file, 'w', encoding='utf-8') as f:
            f.write("password1\npassword2\n")
        
        # Should handle UTF-8 encoded file
        with open(utf8_file, 'r', encoding='utf-8', errors='ignore') as f:
            passwords = [line.strip() for line in f if line.strip()]
            self.assertEqual(len(passwords), 2)
            self.assertIn("password1", passwords)
            self.assertIn("password2", passwords)

    def test_performance_small_password_list(self):
        """Test performance with a small password list"""
        # Create a small password file
        with open(self.password_file, 'w') as f:
            for i in range(100):
                f.write(f"password{i}\n")
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        self.cracker.crack_password(self.test_archive, self.password_file)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        logging.info(f"Small password list test:")
        logging.info(f"Execution time: {execution_time:.2f} seconds")
        logging.info(f"Memory used: {memory_used / 1024 / 1024:.2f} MB")
        
        self.assertLess(execution_time, 5.0)  # Should complete within 5 seconds
        self.assertLess(memory_used, 100 * 1024 * 1024)  # Less than 100MB

    def test_performance_large_password_list(self):
        """Test performance with a large password list"""
        # Create a large password file
        with open(self.password_file, 'w') as f:
            for i in range(10000):
                f.write(f"password{i}\n")
        
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        
        self.cracker.crack_password(self.test_archive, self.password_file)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        execution_time = end_time - start_time
        memory_used = end_memory - start_memory
        
        logging.info(f"Large password list test:")
        logging.info(f"Execution time: {execution_time:.2f} seconds")
        logging.info(f"Memory used: {memory_used / 1024 / 1024:.2f} MB")
        
        # Adjust thresholds based on system capabilities
        self.assertLess(execution_time, 180.0)  # Should complete within 3 minutes
        self.assertLess(memory_used, 1024 * 1024 * 1024)  # Less than 1GB

    @memory_profiler.profile
    def test_memory_usage(self):
        """Test memory usage during password cracking"""
        # Create a medium-sized password file
        with open(self.password_file, 'w') as f:
            for i in range(1000):
                f.write(f"password{i}\n")
        
        self.cracker.crack_password(self.test_archive, self.password_file)
        
        # Memory profiler will automatically log memory usage

    def test_concurrent_workers(self):
        """Test performance with different numbers of workers"""
        # Create a medium-sized password file
        with open(self.password_file, 'w') as f:
            for i in range(1000):
                f.write(f"password{i}\n")
        
        # Test with different numbers of workers
        worker_counts = [1, 2, 4, 8]
        results = []
        
        for workers in worker_counts:
            self.cracker.config["max_workers"] = workers
            start_time = time.time()
            
            self.cracker.crack_password(self.test_archive, self.password_file)
            
            execution_time = time.time() - start_time
            results.append((workers, execution_time))
            
            logging.info(f"Workers: {workers}, Time: {execution_time:.2f} seconds")
        
        # Verify that more workers generally means faster execution
        for i in range(1, len(results)):
            if results[i][0] <= results[i-1][0] * 2:  # Only compare when worker count doubles
                self.assertLessEqual(results[i][1], results[i-1][1] * 1.5)  # Should be at least 33% faster

    def test_integration_full_workflow(self):
        """Test the complete workflow with a real archive"""
        # Create a test archive with a known password
        test_password = "test123"
        archive_path = os.path.join(self.test_dir, "test_integration.7z")
        
        # Create some test files to archive
        test_files_dir = os.path.join(self.test_dir, "test_files")
        os.makedirs(test_files_dir)
        with open(os.path.join(test_files_dir, "test.txt"), 'w') as f:
            f.write("Test content")
        
        # Create password file with the correct password
        with open(self.password_file, 'w') as f:
            f.write("wrong1\nwrong2\n")
            f.write(f"{test_password}\n")
            f.write("wrong3\nwrong4\n")
        
        # Create the archive with 7-Zip
        subprocess.run([
            self.cracker.sevenzip_path,
            "a",
            archive_path,
            os.path.join(test_files_dir, "*"),
            f"-p{test_password}"
        ], capture_output=True)
        
        # Run the password cracker
        self.cracker.crack_password(archive_path, self.password_file)
        
        # Verify the password was found
        self.assertEqual(self.cracker.successful_password, test_password)
        
        # Verify the archive was extracted
        extracted_dir = os.path.join(self.test_dir, self.cracker.config["output_dir"])
        self.assertTrue(os.path.exists(extracted_dir))
        self.assertTrue(os.path.exists(os.path.join(extracted_dir, "test.txt")))

    def test_integration_error_handling(self):
        """Test error handling in real-world scenarios"""
        # Test with corrupted archive
        corrupted_archive = os.path.join(self.test_dir, "corrupted.7z")
        with open(corrupted_archive, 'w') as f:
            f.write("corrupted content")
        
        with open(self.password_file, 'w') as f:
            f.write("test123\n")
        
        # Should handle corrupted archive gracefully
        self.cracker.crack_password(corrupted_archive, self.password_file)
        self.assertIsNone(self.cracker.successful_password)
        
        # Test with empty password file
        empty_password_file = os.path.join(self.test_dir, "empty.txt")
        with open(empty_password_file, 'w') as f:
            f.write("")
        
        # Should handle empty password file
        self.cracker.crack_password(corrupted_archive, empty_password_file)
        self.assertIsNone(self.cracker.successful_password)
        
        # Test with non-existent archive
        non_existent_archive = os.path.join(self.test_dir, "nonexistent.7z")
        with self.assertRaises(FileNotFoundError):
            self.cracker.crack_password(non_existent_archive, self.password_file)
        
        # Test with non-existent password file
        non_existent_password_file = os.path.join(self.test_dir, "nonexistent.txt")
        with self.assertRaises(FileNotFoundError):
            self.cracker.crack_password(corrupted_archive, non_existent_password_file)

if __name__ == '__main__':
    unittest.main() 