from __future__ import annotations

import contextlib
import io
import shlex
import subprocess
import unittest
from unittest.mock import patch

from js_vpn import auth


def saml_output(
    interface: str = "gateway",
    cookie: str = "test-cookie",
    username: str = "user@example.com",
    os_name: str = "linux-64",
) -> str:
    values = {
        "HOST": f"https://gateway.example.com/{interface}:prelogin-cookie",
        "USER": username,
        "COOKIE": cookie,
        "OS": os_name,
    }
    return "\n".join(f"{key}={shlex.quote(value)}" for key, value in values.items())


class AuthenticationTests(unittest.TestCase):
    def test_gateway_cookie_is_only_sent_on_stdin(self):
        cookie = "test-cookie; $(do-not-execute) 'quoted'"
        username = "Example User"
        saml = subprocess.CompletedProcess([], 0, stdout=saml_output(cookie=cookie, username=username))
        connected = subprocess.CompletedProcess([], 0)
        output = io.StringIO()

        with patch.object(auth.subprocess, "run", side_effect=[saml, connected]) as run:
            with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                result = auth.authenticate("vpn.example.com")

        self.assertEqual(result, 0)
        self.assertEqual(run.call_args_list[0].args[0], [
            str(auth.GPSAML), "-q", "--gateway", "--clientos=Linux", "vpn.example.com",
        ])
        self.assertEqual(run.call_args_list[0].kwargs["stdout"], subprocess.PIPE)
        self.assertEqual(run.call_args_list[1].args[0], [
            "sudo", auth.OPENCONNECT,
            f"--csd-wrapper={auth.HIPREPORT}", "--base-mtu=1200", "-b",
            "--protocol=gp", f"--user={username}", "--os=linux-64",
            "--usergroup=gateway:prelogin-cookie", "--passwd-on-stdin",
            "https://gateway.example.com",
        ])
        self.assertEqual(run.call_args_list[1].kwargs["input"], cookie + "\n")
        self.assertNotIn(cookie, output.getvalue())
        self.assertNotIn(cookie, run.call_args_list[1].args[0])

    def test_portal_and_windows_are_available_for_comparison(self):
        saml = subprocess.CompletedProcess([], 0, stdout=saml_output("portal", os_name="win"))
        connected = subprocess.CompletedProcess([], 0)
        with patch.object(auth.subprocess, "run", side_effect=[saml, connected]) as run:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(auth.authenticate("vpn.example.com", "portal", "Windows"), 0)

        self.assertIn("--portal", run.call_args_list[0].args[0])
        self.assertIn("--clientos=Windows", run.call_args_list[0].args[0])
        self.assertIn("--usergroup=portal:prelogin-cookie", run.call_args_list[1].args[0])
        self.assertIn("--os=win", run.call_args_list[1].args[0])

    def test_cancelled_authentication_does_not_start_openconnect(self):
        saml = subprocess.CompletedProcess([], 1, stdout="")
        with patch.object(auth.subprocess, "run", return_value=saml) as run:
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(auth.authenticate("vpn.example.com"), 1)
        run.assert_called_once()

    def test_malformed_saml_output_does_not_start_openconnect(self):
        valid = saml_output()
        responses = [
            "",
            valid + "\nCOOKIE=another-test-cookie",
            valid.replace("USER=user@example.com", "UNKNOWN=user@example.com"),
            valid.replace("https://gateway.example.com", "http://gateway.example.com"),
            valid.replace("https://gateway.example.com", "https://user:password@gateway.example.com"),
            valid.replace("/gateway:", "/portal:"),
            valid.replace("OS=linux-64", "OS=invalid"),
            saml_output(cookie="line-one\nline-two"),
            "HOST='unclosed-quote",
        ]
        for response in responses:
            with self.subTest(response_index=responses.index(response)):
                saml = subprocess.CompletedProcess([], 0, stdout=response)
                with patch.object(auth.subprocess, "run", return_value=saml) as run:
                    with contextlib.redirect_stdout(io.StringIO()):
                        with self.assertRaises(ValueError):
                            auth.authenticate("vpn.example.com")
                    run.assert_called_once()

    def test_invalid_host_is_rejected_before_authentication(self):
        for host in ["", "-vpn.example.com", "vpn.example.com; touch /tmp/unused", "vpn.example.com\n"]:
            with self.subTest(host=host):
                with patch.object(auth.subprocess, "run") as run:
                    with self.assertRaises(ValueError):
                        auth.authenticate(host)
                    run.assert_not_called()

    def test_main_preserves_failure_status_and_shows_error(self):
        with patch.object(auth, "authenticate", return_value=2) as authenticate:
            with patch.object(auth.subprocess, "run") as run:
                self.assertEqual(auth.main(["vpn.example.com"]), 2)
        authenticate.assert_called_once_with("vpn.example.com", "gateway", "Linux")
        self.assertIn("--error", run.call_args.args[0])
        self.assertIn("--text=Falha ao conectar a VPN. Codigo: 2", run.call_args.args[0])

    def test_main_does_not_log_exception_details(self):
        output = io.StringIO()
        with patch.object(auth, "authenticate", side_effect=ValueError("test-secret")):
            with patch.object(auth.subprocess, "run"):
                with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
                    self.assertEqual(auth.main(["vpn.example.com"]), 1)
        self.assertNotIn("test-secret", output.getvalue())


if __name__ == "__main__":
    unittest.main()
