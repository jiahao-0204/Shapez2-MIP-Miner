import colorlog

class CustomColoredFormatter(colorlog.ColoredFormatter):
    def format(self, record):
        # -----------------------------
        # settings
        # -----------------------------

        # color settings
        reset = "\033[0m"
        ip_color = "\033[35m"
        name_colors = {
            "app.webapp": "\033[32m",         # green
            "uvicorn.error": "\033[34m",  # blue
            "uvicorn.access": "\033[34m", # blue
            "watchfiles.main": "\033[31m", # red
        }

        # padding settings
        name_pad_width = 18


        # -----------------------------
        # formatting
        # -----------------------------

        # color ip address
        if record.name == "uvicorn.access":
            # split by first " - "
            parts = record.msg.split(" - ", 1)
            record.msg = f"{ip_color}{parts[0]}{reset} - {parts[1]}"
        
        # color by logger name
        record.name = f"{name_colors.get(record.name, "")}{record.name.ljust(name_pad_width)}{reset}"

        # format the rest
        return super().format(record)
