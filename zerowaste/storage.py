from whitenoise.storage import CompressedManifestStaticFilesStorage

class NonStrictStaticFilesStorage(CompressedManifestStaticFilesStorage):
    # evitar excepción en manifest
    manifest_strict = False