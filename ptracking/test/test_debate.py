import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from unittest import TestCase

from ptracking.scraping.debate import DebateFetcher, DebateText


class TranscriptRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("content-disposition",
                         'attachment; filename="transcript.txt"')
        self.send_header("content-type", "text/plain")
        self.end_headers()
        self.flush_headers()
        self.wfile.write(bytes("Title\r\nText", encoding="utf-8"))


class DebateTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        server = HTTPServer(("", 8000), TranscriptRequestHandler)
        thread = threading.Thread(target=lambda: server.serve_forever())
        thread.start()
        cls.thread = thread
        cls.server = server

    def test_rejects_invalid_url(self):
        with self.assertRaises(KeyError):
            DebateFetcher("invalid_url")

    def test_can_send_request(self):
        url = "http://localhost:8000/{debate_id}"
        fetcher = DebateFetcher(url)
        text = fetcher.fetch_debate_text("id")
        self.assertIsInstance(text, DebateText)
        self.assertEqual(text.title, "Title")
        self.assertEqual(text.content, "Text")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.server.shutdown()
        if cls.thread.is_alive():
            cls.thread.join()
