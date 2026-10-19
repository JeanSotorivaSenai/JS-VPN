from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from js_vpn import vpn


class ConnectionLaunchTests(unittest.TestCase):
    def test_terminal_launch_passes_host_as_an_argument_without_a_shell(self):
        with patch.object(Path, "exists", return_value=True):
            with patch.object(vpn.dns_manager, "backup_dns") as backup:
                with patch.object(vpn.subprocess, "Popen") as popen:
                    self.assertIs(vpn.connect(" vpn.example.com "), popen.return_value)

        backup.assert_called_once_with()
        popen.assert_called_once_with([
            "gnome-terminal",
            f"--working-directory={Path(vpn.__file__).resolve().parent.parent}",
            "--", sys.executable, "-m", "js_vpn.auth", "vpn.example.com",
        ], start_new_session=True)

    def test_invalid_host_does_not_modify_dns_or_start_a_terminal(self):
        with patch.object(vpn.dns_manager, "backup_dns") as backup:
            with patch.object(vpn.subprocess, "Popen") as popen:
                with self.assertRaises(ValueError):
                    vpn.connect("vpn.example.com; false")
        backup.assert_not_called()
        popen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
