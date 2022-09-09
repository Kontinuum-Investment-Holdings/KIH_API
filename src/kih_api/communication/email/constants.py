import os

from kih_api import global_common

email_account = global_common.get_environment_variable("KIH_API_EMAIL_ACCOUNT")
email_account_password = global_common.get_environment_variable("KIH_API_EMAIL_ACCOUNT_PASSWORD")

execution_type__Email_Server = "Email Server"
