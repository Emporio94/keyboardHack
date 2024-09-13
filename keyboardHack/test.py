import unittest
from unittest.mock import patch, MagicMock
import socket
import time
import subprocess

# Import the original script (assuming it's named `connection_detector.py`)
import script_kl as cd


class TestConnectionDetector(unittest.TestCase):

    @patch('connection_detector.socket.gethostbyname')
    def test_resolve_domain_success(self, mock_gethostbyname):
        """Test successful domain name resolution."""
        mock_gethostbyname.return_value = '192.168.1.1'
        
        ip = cd.resolve_domain('example.com')
        self.assertEqual(ip, '192.168.1.1')
        mock_gethostbyname.assert_called_with('example.com')

    @patch('connection_detector.socket.gethostbyname', side_effect=socket.gaierror)
    def test_resolve_domain_failure(self, mock_gethostbyname):
        """Test failure of domain name resolution."""
        ip = cd.resolve_domain('invalid.domain')
        self.assertIsNone(ip)
        mock_gethostbyname.assert_called_with('invalid.domain')

    @patch('connection_detector.subprocess.check_output')
    @patch('connection_detector.custom_action')
    def test_check_connections(self, mock_custom_action, mock_check_output):
        """Test connection detection and response."""
        # Mock the output of `netstat -n` to simulate an established connection.
        mock_check_output.return_value = b"""
        Proto  Local Address          Foreign Address        State
        TCP    127.0.0.1:12345        192.168.1.1:80         ESTABLISHED
        """

        # Define mock target IPs (this mimics the resolved IPs from the main script).
        cd.target_ips = {'example.com': '192.168.1.1'}

        # Run the check_connections function in a single loop (patching time.sleep to avoid actual delay).
        with patch('time.sleep', return_value=None):
            cd.check_connections()

        # Check that custom_action was called with the right IP and domain.
        mock_custom_action.assert_called_with('192.168.1.1', 'example.com')

    @patch('connection_detector.subprocess.check_output', side_effect=subprocess.CalledProcessError(1, 'netstat -n'))
    def test_check_connections_netstat_error(self, mock_check_output):
        """Test handling of a `netstat` command error."""
        # Simulate a failure when running `netstat`.
        with patch('time.sleep', return_value=None), patch('builtins.print') as mock_print:
            cd.check_connections()

        # Verify that the error message was printed.
        mock_print.assert_any_call("Error running netstat command")


if __name__ == '__main__':
    unittest.main()
