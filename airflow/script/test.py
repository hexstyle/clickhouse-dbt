from metadata.generated.schema.entity.services.connections.metadata.openMetadataConnection import (
    OpenMetadataConnection,
)
from metadata.generated.schema.security.client.openMetadataJWTClientConfig import (
    OpenMetadataJWTClientConfig,
)
from metadata.ingestion.ometa.ometa_api import OpenMetadata

server_config = OpenMetadataConnection(
    hostPort="http://openmetadata:8585/api",
    authProvider="openmetadata",
    securityConfig=OpenMetadataJWTClientConfig(
        jwtToken="eyJhbGciOiJSUzI1NiIsImtpZCI6ImdiMzg5YS05Zjc2LWdkanMtYTkyai0wMjQyYms5NDM1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJsb2NhbGhvc3QiLCJzdWIiOiJhaXJmbG93IiwiYXVkIjoibG9jYWxob3N0IiwiZXhwIjoxNzc2ODk1NDcyLCJpYXQiOjE3NDA4OTkwNzJ9.UWN_Fq7NTo8r1xD6m-5QsCzysS60SGNcvJ7i5iFjvmtogahJtbJtuDqs7H_3UOu4wvbm3HLmwkqVmQiD6trDkV3KOfriGmD3LUjRSztTptRmKaRJN5F37PxtFEfxXXbNKJnCMEle0et9XN1_aBC7Tf0EVeVrfWHAzK8sc9FrMll0g1cO3aWE0gNtvtPhkK7Zj_SawxQFzle1RkFzmcbEiI1vvGExU2BEZOS7DD2FpZ5zDizNdb0_6LMBlsxaW8H8yEP6tTOkTSVc5qPH6AwIdgtCwXFJV0SuQR6yKASm5TBDDwLL9AeRCZIAG2tWL1oyvo2U3IqkQ2MqSvSPwf-PaQ"
    ),
)
metadata = OpenMetadata(server_config)

assert metadata.health_check()