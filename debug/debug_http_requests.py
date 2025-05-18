# %% Imports
import importlib
import azure.identity
from azure.keyvault.secrets import SecretClient
import garth

importlib.reload(garth)

# %% Constants
KEY_VAULT_URL = "https://healthhubvault.vault.azure.net/"
GARMIN_USERNAME_SECRET_NAME = "GarminUsername"
GARMIN_PASSWORD_SECRET_NAME = "GarminPassword"

# %% Fetch Garmin credentials from Azure Key Vault using Az PS credentials
credential = azure.identity.AzurePowerShellCredential()
key_vault_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)
username = key_vault_client.get_secret(GARMIN_USERNAME_SECRET_NAME).value
password = key_vault_client.get_secret(GARMIN_PASSWORD_SECRET_NAME).value

# %% Log into Garmin via garth (Should show a debug message)
print('Logging into Garmin...')
garth.login(username, password)
print('Log in complete.')

# %% Get heart rate zones 
garth.connectapi('/biometric-service/heartRateZones')

# %%
