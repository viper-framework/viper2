# Copyright 2023 The viper2 Authors. All rights reserved.
# Use of this source code is governed by a BSD-style
# license that can be found in the LICENSE file.

def sanitize_url(url: str) -> str:
    return url.replace("http", "hxxp").replace(".", "[.]")
