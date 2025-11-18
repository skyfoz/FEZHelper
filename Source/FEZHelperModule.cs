using System;

namespace Celeste.Mod.FEZHelper;

public class FEZHelperModule : EverestModule {
    public static FEZHelperModule Instance { get; private set; }

    public override Type SettingsType => typeof(FEZHelperModuleSettings);
    public static FEZHelperModuleSettings Settings => (FEZHelperModuleSettings) Instance._Settings;

    public override Type SessionType => typeof(FEZHelperModuleSession);
    public static FEZHelperModuleSession Session => (FEZHelperModuleSession) Instance._Session;

    public override Type SaveDataType => typeof(FEZHelperModuleSaveData);
    public static FEZHelperModuleSaveData SaveData => (FEZHelperModuleSaveData) Instance._SaveData;

    public FEZHelperModule() {
        Instance = this;
#if DEBUG
        // debug builds use verbose logging
        Logger.SetLogLevel(nameof(FEZHelperModule), LogLevel.Verbose);
#else
        // release builds use info logging to reduce spam in log files
        Logger.SetLogLevel(nameof(FEZHelperModule), LogLevel.Info);
#endif
    }

    public override void Load() {
        // TODO: apply any hooks that should always be active
    }

    public override void Unload() {
        // TODO: unapply any hooks applied in Load()
    }
}