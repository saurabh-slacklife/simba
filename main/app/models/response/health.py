"""
Health Check model response object to be used by Main application and any other dependent or Downstream application
"""


class Health:
    def __init__(self):
        self._health_status = "Unknown"
        self._health_header = "Unknown"

    @property
    def health_status(self):
        return self._health_status

    @health_status.setter
    def health_status(self, value):
        self._health_status = value

    @property
    def health_header(self):
        return self._health_header

    @health_header.setter
    def health_header(self, value):
        self._health_header = value
