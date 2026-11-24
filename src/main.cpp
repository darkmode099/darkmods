#include <orbis/libkernel.h>
#include <orbis/Sysmodule.h>
#include <orbis/SystemService.h>
#include <orbis/UserService.h>
#include <orbis/Pad.h>
#include <orbis/VideoOut.h>
#include <unistd.h>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <cstdint>

struct LoaderState {
    int progress;          // 0 -> 100
    bool finished;         // ينتقل للواجهة عند الاكتمال
};

struct UiState {
    int selectedIndex;     // 0 = تثبيت المود, 1 = خروج
    int pressPulseFrames;  // مدة تأثير نبضة/توهج ضغطة زر X
    bool actionTriggered;
    bool installDone;
    int installedTargets;
    bool modBannerShown;
};

static void sendConsoleActivationMessage(const char* messageText) {
    std::printf("\n================================================\n");
    std::printf("[Blaze 100 NOTIFICATION] %s\n", messageText);
    std::printf("================================================\n");
    std::fflush(stdout);
}

static bool copySingleFile(const char* srcPath, const char* dstPath) {
    FILE* in = std::fopen(srcPath, "rb");
    if (!in) {
        return false;
    }

    FILE* out = std::fopen(dstPath, "wb");
    if (!out) {
        std::fclose(in);
        return false;
    }

    unsigned char buf[65536];
    size_t readBytes = 0;
    bool ok = true;

    while ((readBytes = std::fread(buf, 1, sizeof(buf), in)) > 0) {
        if (std::fwrite(buf, 1, readBytes, out) != readBytes) {
            ok = false;
            break;
        }
    }

    std::fclose(in);
    std::fclose(out);
    return ok;
}

static const char* findExistingSource(const char* const* candidates, size_t count) {
    for (size_t i = 0; i < count; ++i) {
        FILE* test = std::fopen(candidates[i], "rb");
        if (test) {
            std::fclose(test);
            return candidates[i];
        }
    }
    return nullptr;
}

static int installScorpionModToConsole() {
    const char* prxSources[] = {
        "/app0/sce_sys/ScorpionMenu-v1.2b-100US.prx",
        "/app0/prx/ScorpionMenu-v1.2b-100US.prx",
        "assets/ScorpionMenu-v1.2b-100US.prx"
    };

    const char* themeSources[] = {
        "/app0/sce_sys/Blaze100_Theme.ini",
        "mod_data/CUSA00419/Blaze100_Theme.ini"
    };

    const char* menuArSources[] = {
        "/app0/sce_sys/Blaze100_Menu_AR.txt",
        "mod_data/CUSA00419/Blaze100_Menu_AR.txt"
    };

    const char* targetDirs[] = {
        "/data/GoldHEN",
        "/data/GoldHEN/plugins",
        "/data/mods",
        "/data/mods/CUSA00419",
        "/data/CUSA00419"
    };

    const char* prxTargets[] = {
        "/data/GoldHEN/ScorpionMenu-v1.2b-100US.prx",
        "/data/GoldHEN/plugins/ScorpionMenu-v1.2b-100US.prx",
        "/data/mods/ScorpionMenu-v1.2b-100US.prx",
        "/data/mods/CUSA00419/ScorpionMenu-v1.2b-100US.prx",
        "/data/CUSA00419/ScorpionMenu-v1.2b-100US.prx"
    };

    const char* themeTargets[] = {
        "/data/GoldHEN/Blaze100_Theme.ini",
        "/data/mods/CUSA00419/Blaze100_Theme.ini"
    };

    const char* menuArTargets[] = {
        "/data/GoldHEN/Blaze100_Menu_AR.txt",
        "/data/mods/CUSA00419/Blaze100_Menu_AR.txt"
    };

    const char* activePrx = findExistingSource(prxSources, sizeof(prxSources) / sizeof(prxSources[0]));
    if (!activePrx) {
        std::printf("[Blaze 100] ScorpionMenu PRX source not found\n");
        std::fflush(stdout);
        return 0;
    }

    const char* activeTheme = findExistingSource(themeSources, sizeof(themeSources) / sizeof(themeSources[0]));
    const char* activeMenuAr = findExistingSource(menuArSources, sizeof(menuArSources) / sizeof(menuArSources[0]));

    for (size_t d = 0; d < sizeof(targetDirs) / sizeof(targetDirs[0]); ++d) {
        char cmd[512];
        std::snprintf(cmd, sizeof(cmd), "mkdir -p \"%s\" 2>/dev/null", targetDirs[d]);
        std::system(cmd);
    }

    int successCount = 0;
    for (size_t t = 0; t < sizeof(prxTargets) / sizeof(prxTargets[0]); ++t) {
        if (copySingleFile(activePrx, prxTargets[t])) {
            successCount++;
            std::printf("[Blaze 100] Installed PRX -> %s\n", prxTargets[t]);
        }
    }

    if (activeTheme) {
        for (size_t i = 0; i < sizeof(themeTargets) / sizeof(themeTargets[0]); ++i) {
            if (copySingleFile(activeTheme, themeTargets[i])) {
                successCount++;
                std::printf("[Blaze 100] Installed Theme -> %s\n", themeTargets[i]);
            }
        }
    }

    if (activeMenuAr) {
        for (size_t i = 0; i < sizeof(menuArTargets) / sizeof(menuArTargets[0]); ++i) {
            if (copySingleFile(activeMenuAr, menuArTargets[i])) {
                successCount++;
                std::printf("[Blaze 100] Installed Arabic Menu -> %s\n", menuArTargets[i]);
            }
        }
    }

    std::fflush(stdout);
    return successCount;
}

static void runFastLoadingBar(LoaderState& loader, int totalDurationMs = 2000) {
    const int steps[] = {0, 20, 50, 80, 100};
    const int numSteps = sizeof(steps) / sizeof(steps[0]);
    int stepDelayUs = (totalDurationMs * 1000) / numSteps;

    loader.progress = 0;
    loader.finished = false;

    for (int i = 0; i < numSteps; ++i) {
        loader.progress = steps[i];
        std::printf("[Blaze 100] Loading: %d%%\n", loader.progress);
        std::fflush(stdout);
        usleep(stepDelayUs);
    }

    loader.finished = true;
}

static void triggerButtonPressEffect(UiState& ui, int buttonIndex) {
    ui.selectedIndex = buttonIndex;
    ui.pressPulseFrames = 12;
    ui.actionTriggered = true;

    for (int f = ui.pressPulseFrames; f > 0; --f) {
        std::printf("[Blaze 100] Button %d X-Press FX intensity=%d\n", buttonIndex, f);
        std::fflush(stdout);
        usleep(25000);
    }

    if (buttonIndex == 0) {
        ui.installedTargets = installScorpionModToConsole();
        ui.installDone = (ui.installedTargets > 0);
        ui.modBannerShown = true;
        sendConsoleActivationMessage("Blaze 100 | ScorpionMenu Activated for GTA V v1.00 (CUSA00419)");
    }
}

static void loadOptionalSysmodules() {
#ifdef ORBIS_SYSMODULE_SYSTEM_SERVICE
    sceSysmoduleLoadModule(ORBIS_SYSMODULE_SYSTEM_SERVICE);
#endif
#ifdef ORBIS_SYSMODULE_USER_SERVICE
    sceSysmoduleLoadModule(ORBIS_SYSMODULE_USER_SERVICE);
#endif
#ifdef ORBIS_SYSMODULE_PAD
    sceSysmoduleLoadModule(ORBIS_SYSMODULE_PAD);
#endif
#ifdef ORBIS_SYSMODULE_VIDEO_OUT
    sceSysmoduleLoadModule(ORBIS_SYSMODULE_VIDEO_OUT);
#endif
}

int main() {
    loadOptionalSysmodules();

    sceUserServiceInitialize(nullptr);
    OrbisUserServiceLoginUserIdList userList;
    std::memset(&userList, 0, sizeof(userList));
    sceUserServiceGetLoginUserIdList(&userList);
    int userId = userList.userId[0];

    scePadInit();
    int padHandle = scePadOpen(userId, 0, 0, nullptr);

#ifdef ORBIS_VIDEO_OUT_BUS_MAIN
    int videoHandle = sceVideoOutOpen(userId, ORBIS_VIDEO_OUT_BUS_MAIN, 0, nullptr);
    if (videoHandle >= 0) {
        OrbisVideoOutBufferAttribute attr;
        std::memset(&attr, 0, sizeof(attr));
        sceVideoOutSetBufferAttribute(&attr, 0, 1920, 1080, 1920, 0, 0);
    }
#endif

    LoaderState loader;
    runFastLoadingBar(loader, 2000);

#ifdef sceSystemServiceHideSplashScreen
    sceSystemServiceHideSplashScreen();
#endif

    UiState ui{0, 0, false, false, 0, false};
    OrbisPadData padData;

    unsigned int btnUp =
#ifdef ORBIS_PAD_BUTTON_UP
        ORBIS_PAD_BUTTON_UP;
#else
        0x00000010u;
#endif

    unsigned int btnDown =
#ifdef ORBIS_PAD_BUTTON_DOWN
        ORBIS_PAD_BUTTON_DOWN;
#else
        0x00000040u;
#endif

    unsigned int btnCross =
#ifdef ORBIS_PAD_BUTTON_CROSS
        ORBIS_PAD_BUTTON_CROSS;
#else
        0x00004000u;
#endif

    while (true) {
        if (padHandle >= 0) {
            std::memset(&padData, 0, sizeof(padData));
            if (scePadReadState(padHandle, &padData) == 0 && padData.connected) {
                unsigned int buttons = padData.buttons;

                if (buttons & btnUp) {
                    ui.selectedIndex = 0;
                } else if (buttons & btnDown) {
                    ui.selectedIndex = 1;
                }

                if (buttons & btnCross) {
                    triggerButtonPressEffect(ui, ui.selectedIndex);
                    if (ui.selectedIndex == 1) {
                        break;
                    }
                }
            }
        }

        if (ui.pressPulseFrames > 0) {
            ui.pressPulseFrames--;
        }

        usleep(16666);
    }

    if (padHandle >= 0) {
        scePadClose(padHandle);
    }
    sceUserServiceTerminate();
    return 0;
}
