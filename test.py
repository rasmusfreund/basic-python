import pytest
import subprocess
import sys
import os

class TestUtilities:
    def test_python_syntax(self, src_path="src"):
        if not os.path.exists(src_path):
            pytest.skip(f"Source directory {src_path} does not exist")
        
        python_files = [f for f in os.listdir(src_path) if f.endswith('.py')]
        
        for filename in python_files:
            filepath = os.path.join(src_path, filename)
            try:
                with open(filepath, 'r') as f:
                    compile(f.read(), filepath, 'exec')
            except SyntaxError as e:
                pytest.fail(f"Syntax error in {filename}: {e}")
            except Exception as e:
                # File could have import issues or runtime errors, which is OK for syntax checking
                pass

class TestBasicProgramming:
    
    @pytest.fixture
    def src_path(self):
        return os.path.join(os.getcwd(), 'src')
    
    def run_python_file(self, filepath, input_data=None, timeout=10):
        try:
            if input_data:
                result = subprocess.run(
                    [sys.executable, filepath],
                    input=input_data,
                    text=True,
                    capture_output=True,
                    timeout=timeout
                )
            else:
                result = subprocess.run(
                    [sys.executable, filepath],
                    text=True,
                    capture_output=True,
                    timeout=timeout
                )
            return result.stdout.strip(), result.stderr.strip(), result.returncode
        except subprocess.TimeoutExpired:
            return None, "Process timed out", -1
        except Exception as e:
            return None, str(e), -1
    
    
    def run_and_check_file(self, src_path, filename, input_data=None, timeout=10):
        filepath = os.path.join(src_path, filename)
        if not os.path.exists(filepath):
            pytest.skip(f"{filepath} does not exist")
            
        stdout, stderr, returncode = self.run_python_file(filepath, input_data, timeout)
        
        if returncode != 0:
            pytest.fail(f"Script {filename} failed with error: {stderr}")
        
        return stdout, stderr, returncode 
    
    
    def test_file_structure(self, src_path):
        expected_files = [
            'hello.py',
            'hello-n.py',
            'do-you-want-to-stop.py',
            'print-1-10.py',
            'print-1-10-growing.py',
            'pattern.py',
            'lists.py',
            'counts.py',
            'password.py',
            'hex.py'
        ]
        
        existing_files = []
        missing_files = []
        
        for filename in expected_files:
            filepath = os.path.join(src_path, filename)
            if os.path.exists(filepath):
                existing_files.append(filename)
            else:
                missing_files.append(filename)
                
        assert len(existing_files) > 0, f"No expected ffiles found in {src_path}"
        
        if missing_files:
            print(f"\nMissing files: {missing_files}")
            print(f"Existing files: {existing_files}")
    
    
    def test_hello_world(self, src_path):
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'hello.py')
        assert stdout == "Hello, World!", f"Expected 'Hello, World!', got '{stdout}'"
        
        
    def test_hello_n(self, src_path):            
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'hello-n.py', input_data="3\n")
        
        hello_count = stdout.count("Hello, World!")
        assert hello_count == 3, f"Expected 3 'Hello, World!' occurrences, got {hello_count}\nFull output: {repr(stdout)}"
        
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'hello-n.py', input_data="1\n")
        assert returncode == 0, f"Script failed with error: {stderr}"
        
        hello_count = stdout.count("Hello, World!")
        assert hello_count == 1, f"Expected 1 'Hello, World!' occurrence, got {hello_count}\nFull output: {repr(stdout)}"
        
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'hello-n.py', input_data="0\n")
        assert returncode == 0, f"Script failed with error: {stderr}"
        
        hello_count = stdout.count("Hello, World!")
        assert hello_count == 0, f"Expected 0 'Hello, World!' occurrences for n=0, got {hello_count}\nFull output: {repr(stdout)}"
        
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'hello-n.py', input_data="5\n")
        assert returncode == 0, f"Script failed with error: {stderr}"
        
        hello_count = stdout.count("Hello, World!")
        assert hello_count == 5, f"Expected 5 'Hello, World!' occurrences, got {hello_count}\nFull output: {repr(stdout)}"
    
    
    def test_do_you_want_to_stop(self, src_path):
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'do-you-want-to-stop.py', input_data="no\nno\nyes\n")
        
        question_count = stdout.lower().count("do you want to stop?")
        assert question_count >= 3, f"Expected at least 3 'Do you want to stop?' prompts, found {question_count}"
        
        stdout2, stderr2, returncode2 = self.run_and_check_file(src_path, 'do-you-want-to-stop.py', input_data="yes\n")  
    
    
    def test_print_1_10(self, src_path):
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'print-1-10.py')
                
        lines = [line.strip() for line in stdout.split('\n') if line.strip()]
        expected = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10']
        assert lines == expected, f"Expected {expected}, got {lines}"
    
    
    def test_print_1_10_growing(self, src_path):
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'print-1-10-growing.py')
        
        lines = stdout.split('\n')
        
        expected = [
            '1',
            '1 2',
            '1 2 3',
            '1 2 3 4',
            '1 2 3 4 5',
            '1 2 3 4 5 6',
            '1 2 3 4 5 6 7',
            '1 2 3 4 5 6 7 8',
            '1 2 3 4 5 6 7 8 9',
            '1 2 3 4 5 6 7 8 9 10'            
        ]
        
        actual_lines = [line for line in lines if line.strip()]
        assert actual_lines == expected, f"Expected pattern doesn't match. Got:\n{chr(10).join(actual_lines)}"
    
    
    def test_pattern(self, src_path):
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'pattern.py')
        
        lines = stdout.split('\n')
        
        expected = [
            '*',
            '* *',
            '* * *',
            '* * * *',
            '* * * * *',
            '* * * *',
            '* * *',
            '* *',
            '*'
        ]
        
        actual_lines = [line.rstrip() for line in lines if line.strip()]
        assert actual_lines == expected, f"Star pattern doesn't match. Expected:\n{chr(10).join(expected)}\nGot:\n{chr(10).join(actual_lines)}"
    
    
    def test_lists(self, src_path):
        filepath = os.path.join(src_path, 'lists.py')
        if not os.path.exists(filepath):
            pytest.skip(f"{filepath} does not exist")
            
        result = subprocess.run(
            [sys.executable, filepath, "mean", "1", "2", "3", "4", "5", "6"],
            text=True, capture_output=True
        )
        stdout, stderr, returncode = result.stdout.strip(), result.stderr.strip(), result.returncode
        assert returncode == 0, f"Mean script failed with error: {stderr}"
        
        try:
            mean_value = float(stdout)
            expected_mean = 3.5
            assert abs(mean_value - expected_mean) < 0.001, f"Expected mean 3.5, got {mean_value}"
        except ValueError:
            pytest.fail(f"Mean output is not a valid number: '{stdout}'")
            
        
        result = subprocess.run(
            [sys.executable, filepath, "times", "1", "2", "3"],
            text=True, capture_output=True
        )
        stdout, stderr, returncode = result.stdout.strip(), result.stderr.strip(), result.returncode
        assert returncode == 0, f"Mean script failed with error: {stderr}"

        expected_times = "3 6 9"
        assert stdout == expected_times, f"Expected '{expected_times}', got '{stdout}'"
        
        
        result = subprocess.run(
            [sys.executable, filepath, "even", "1", "2", "3", "4", "5", "6"],
            text=True, capture_output=True
        )
        stdout, stderr, returncode = result.stdout.strip(), result.stderr.strip(), result.returncode
        
        assert returncode == 0, f"Even script failed with error: {stderr}"
        
        expected_even = "2 4 6"
        assert stdout == expected_even, f"Expected '{expected_even}', got '{stdout}'"
        

        result = subprocess.run(
            [sys.executable, filepath, "invalid_command", "1", "2"],
            text=True, capture_output=True
        )
        assert result.returncode != 0, "Should fail with invalid command"
        
        
        result = subprocess.run(
            [sys.executable, filepath],
            text=True, capture_output=True
        )
        assert result.returncode != 0, "Should fail with no arguments"
    
    
    def test_count(self, src_path):
        stdout, stderr, returncode = self.run_and_check_file(src_path, 'counts.py', input_data='hello\n')
        
        output = stdout.lower()
        assert 'h' in output and 'e' in output and 'l' in output and 'o' in output, \
            f"Character counts not found in output: {stdout}"
        
        
    def test_password_validation(self, src_path):
        filepath = os.path.join(src_path, 'password.py')
        if not os.path.exists(filepath):
            pytest.skip(f"{filepath} does not exist")
        
        # Try command-line argument first
        try:
            result_valid = subprocess.run(
                [sys.executable, filepath, "Abc123#"],
                text=True, capture_output=True
            )
            
            result_invalid = subprocess.run(
                [sys.executable, filepath, "Ab1#"],
                text=True, capture_output=True
            )
            
            if result_valid.returncode == 0 and result_invalid.returncode == 0:
                stdout_valid = result_valid.stdout.strip()
                stdout_invalid = result_invalid.stdout.strip()
                
                assert stdout_valid != stdout_invalid or "valid" in stdout_valid.lower() or "invalid" in stdout_invalid.lower(), \
                    f"Password validation doesn't distinguish between valid and invalid passwords. Valid: '{stdout_valid}', Invalid: '{stdout_invalid}'"
                return
        
        except Exception:
            pass  # Fall back to stdin approach
        
        try:
            stdout, stderr, returncode = self.run_and_check_file(src_path, 'password.py', input_data="Abc123#\n")
            
            stdout2, stderr2, returncode2 = self.run_and_check_file(src_path, 'password.py', input_data="Ab1#\n")
            
            assert stdout != stdout2 or "valid" in stdout.lower() or "invalid" in stdout2.lower(), \
            "Password validation doesn't seem to distinguish between valid and invalid passwords"
        
        except Exception as e:
            pytest.fail(f"Password validation test failed. Last error: {e}")
        
        
    def test_hex_encoding_decoding(self, src_path):
        filepath = os.path.join(src_path, 'hex.py')
        if not os.path.exists(filepath):
            pytest.skip(f"{filepath} does not exist")
        
        result_enc = subprocess.run(
            [sys.executable, filepath, "encode", "abcdabc"],
            text=True, capture_output=True
        )
        stdout_enc, stderr_enc, returncode_enc = result_enc.stdout.strip(), result_enc.stderr.strip(), result_enc.returncode
        
        assert returncode_enc == 0, f"Encoding failed with error: {stderr_enc}"
        assert stdout_enc, "No encoding output produced"
        assert "0x" in stdout_enc, "Hex encoding should contain '0x' markers"
        
        print(f"\nDEBUG: Encoded '{repr('abcdabc')}' to '{repr(stdout_enc)}'")
        
        encoded_value = stdout_enc
        result_dec = subprocess.run(
            [sys.executable, filepath, "decode", encoded_value],
            text=True, capture_output=True
        )
        stdout_dec, stderr_dec, returncode_dec = result_dec.stdout.strip(), result_dec.stderr.strip(), result_dec.returncode
        
        assert returncode_dec == 0, f"Decoding failed with error: {stderr_dec}"
        
        print(f"DEBUG: Decoded '{repr(encoded_value)}' to '{repr(stdout_dec)}'")
        print(f"DEBUG: Expected '{repr('abcdabc')}', got '{repr(stdout_dec)}'")
        print(f"DEBUG: Are they equal? {stdout_dec == 'abcdabc'}")
        print(f"DEBUG: Length - expected: {len('abcdabc')}, got: {len(stdout_dec)}")
        
        assert stdout_dec == "abcdabc", f"Expected {repr('abcdabc')}, got {repr(stdout_dec)}"
        
        result_enc2 = subprocess.run(
            [sys.executable, filepath, "encode", "hello"],
            text=True, capture_output=True
        )
        
        if result_enc2.returncode == 0:
            encoded_hello = result_enc2.stdout.strip()
            result_dec2 = subprocess.run(
                [sys.executable, filepath, "decode", encoded_hello],
                text=True, capture_output=True
            )
            
            if result_dec2.returncode == 0:
                assert result_dec2.stdout.strip() == "hello", \
                    f"Round-trip test failed: 'hello' -> '{encoded_hello}' -> '{result_dec2.stdout.strip()}'"

if __name__ == '__main__':
    pytest.main([__file__, "-v", "--tb=short"])