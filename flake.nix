{
  description = "volt-gui - Vulkan game control panel";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  };

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";

      pkgs = import nixpkgs {
        inherit system;
      };

      lib = pkgs.lib;

      cargoToml =
        builtins.fromTOML
          (builtins.readFile ./Cargo.toml);

      version = cargoToml.package.version;

      commonRustArgs = {
        pname = "volt";
        inherit version;

        src = ./.;

        cargoLock = {
          lockFile = ./Cargo.lock;
        };

        doCheck = false;
      };

      # 64-bit layer, launcher, and probe
      volt64 = pkgs.rustPlatform.buildRustPackage (
        commonRustArgs
        // {
          buildInputs = [
            pkgs.libxcb
          ];

          installPhase = ''
            runHook preInstall

            mkdir -p $out/bin $out/lib

            install -Dm755 \
              "$(find target -type f -name volt -perm -0100 -print -quit)" \
              $out/bin/volt

            install -Dm755 \
              "$(find target -type f -name volt-probe -perm -0100 -print -quit)" \
              $out/bin/volt-probe

            install -Dm755 \
              "$(find target -type f -name libvolt.so -print -quit)" \
              $out/lib/libvolt.so

            runHook postInstall
          '';
        }
      );

      # 32-bit Vulkan layer
      volt32 = pkgs.pkgsi686Linux.rustPlatform.buildRustPackage (
        commonRustArgs
        // {
          pname = "volt-layer-32";

          cargoBuildFlags = [
            "--lib"
          ];

          installPhase = ''
            runHook preInstall

            mkdir -p $out/lib

            install -Dm755 \
              "$(find target -type f -name libvolt.so -print -quit)" \
              $out/lib/libvolt.so

            runHook postInstall
          '';
        }
      );

      pythonEnv = pkgs.python3.withPackages (ps: [
        ps.pyside6
      ]);

      volt-gui = pkgs.stdenvNoCC.mkDerivation {
        pname = "volt-gui";
        inherit version;

        src = ./.;

        nativeBuildInputs = [
          pkgs.makeWrapper
          pkgs.qt6.wrapQtAppsHook
        ];

        buildInputs = [
          pkgs.qt6.qtbase
          pkgs.qt6.qtwayland
        ];

        dontWrapQtApps = true;
        dontConfigure = true;
        dontBuild = true;

        installPhase = ''
          runHook preInstall

          install -Dm755 \
            ${volt64}/lib/libvolt.so \
            $out/lib/volt/x86_64-linux-gnu/libvolt.so

          install -Dm755 \
            ${volt32}/lib/libvolt.so \
            $out/lib/volt/i386-linux-gnu/libvolt.so

          install -Dm644 \
            VkLayer_volt.json \
            $out/share/vulkan/implicit_layer.d/VkLayer_volt.json

          mkdir -p $out/share/volt-gui
          cp -r volt-gui/. $out/share/volt-gui/

          install -Dm644 \
            images/1.png \
            $out/share/icons/hicolor/256x256/apps/volt-gui.png

          mkdir -p $out/share/applications

          cat > $out/share/applications/volt-gui.desktop <<EOF
          [Desktop Entry]
          Type=Application
          Version=1.0
          Name=volt-gui
          Comment=Vulkan game control panel
          Exec=volt-gui
          Icon=volt-gui
          Terminal=false
          Categories=Utility;
          Keywords=vulkan;vsync;gpu;gaming;
          StartupNotify=true
          StartupWMClass=volt-gui
          EOF

          # volt expects both layer directories on LD_LIBRARY_PATH.
          makeWrapper ${volt64}/bin/volt $out/bin/volt \
            --prefix LD_LIBRARY_PATH : \
              "$out/lib/volt/x86_64-linux-gnu:$out/lib/volt/i386-linux-gnu" \
            --prefix VK_ADD_IMPLICIT_LAYER_PATH : \
              "$out/share/vulkan/implicit_layer.d"

          # ash loads libvulkan dynamically.
          makeWrapper ${volt64}/bin/volt-probe $out/bin/volt-probe \
            --prefix LD_LIBRARY_PATH : \
              "${lib.makeLibraryPath [ pkgs.vulkan-loader ]}"

          makeWrapper ${pythonEnv}/bin/python $out/bin/volt-gui \
            ''${qtWrapperArgs[@]} \
            --prefix PATH : "$out/bin" \
            --add-flags "$out/share/volt-gui/volt-gui.py"

          runHook postInstall
        '';

        meta = {
          description = "Control panel for Vulkan games on Linux";
          homepage = "https://github.com/pythonlover02/volt-gui";
          license = lib.licenses.gpl3Only;
          platforms = [ "x86_64-linux" ];
          mainProgram = "volt-gui";
        };
      };
    in
    {
      packages.${system} = {
        default = volt-gui;
        volt-gui = volt-gui;
      };

      apps.${system} = {
        default = {
          type = "app";
          program = "${volt-gui}/bin/volt-gui";
        };

        volt-gui = {
          type = "app";
          program = "${volt-gui}/bin/volt-gui";
        };
      };
    };
}
