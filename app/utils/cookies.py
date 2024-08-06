class CookieConverter:
    """
    A class to convert Netscape format cookies to a cookie-list name-value string.
    """

    def __init__(self, netscape_cookie):
        """
        Initialize the CookieConverter with a Netscape format cookie string.

        :param netscape_cookie: A string containing cookies in Netscape format.
        """
        self.netscape_cookie = netscape_cookie

    def convert(self):
        """
        Convert the Netscape cookie to a cookie-list name-value string.

        :return: A string representing the cookies in name-value format.
        """
        cookie_str = ""
        lines = [line for line in self.netscape_cookie.split('\n') if ".youtube" in line]
        for line in lines:
            name, value = line.split("\t")[5:7]
            cookie_str += f"{name}={value}; "

        return cookie_str.rstrip("; ")
