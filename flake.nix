{
  description = "volt-gui - Vulkan settings layer + PySide6 control panel";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem (system:
      let
        pkgs = import nixpkgs { inherit system; };

        version = "2.3.1";

        # --- Rust part: libvolt.so (cdylib) + volt + volt-probe ---
        volt-layer = pkgs.rustPlatform.buildRustPackage {
          pname = "volt-layer";
          inherit version;
          src = ./.;

          cargoLock.lockFile = ./Cargo.lock;

          # cdylib + bins; skip tests (needs GPU/vulkan loader)
          doCheck = false;

          # rustPlatform installs bins automatically; also install cdylib
          postInstall = ''
            mkdir -p $out/lib
            # find the built cdylib (release, host triple)
            lib=$(find target/*/release -maxdepth 1 -name "libvolt.so" | head -n1)
            install -Dm755 "$lib" $out/lib/libvolt.so
          '';
        };

        pythonEnv = pkgs.python3.withPackages (ps: with ps; [ pyside6 ]);

      in {
        packages = rec {
          default = volt-gui;

          inherit volt-layer;

          volt-gui = pkgs.stdenv.mkDerivation {
            pname = "volt-gui";
            inherit version;
            src = ./.;

            nativeBuildInputs = with pkgs; [ makeWrapper qt6.wrapQtAppsHook ];
            buildInputs = [ volt-layer pythonEnv pkgs.qt6.qtbase pkgs.qt6.qtwayland ];
            propagatedBuildInputs = [ pythonEnv ];
            dontConfigure = true;
            dontBuild = true;

            installPhase = ''
              runHook preInstall

              mkdir -p $out/bin $out/share/volt-gui
              cp -r src/volt-gui/*.py $out/share/volt-gui/
              cp ${volt-layer}/bin/volt $out/bin/volt
              cp ${volt-layer}/bin/volt-probe $out/bin/volt-probe
              chmod +x $out/bin/volt $out/bin/volt-probe

              # wrapper: GUI precisa achar volt/volt-probe + PySide6 + Qt plugins
              makeWrapper ${pythonEnv}/bin/python $out/bin/volt-gui \
                --prefix PATH : "${pkgs.lib.makeBinPath [ volt-layer ]}" \
                --prefix PYTHONPATH : "$out/share/volt-gui" \
                --add-flags "$out/share/volt-gui/volt-gui.py" \
                --set QT_QPA_PLATFORM "xcb;wayland" \
                "''${qtWrapperArgs[@]}"

              # --- Vulkan implicit layer manifest (path absoluto, exigido pelo loader) ---
              mkdir -p $out/share/vulkan/implicit_layer.d
              ${pkgs.jq}/bin/jq \
                --arg path "${volt-layer}/lib/libvolt.so" \
                '.layer.library_path = $path' \
                $src/VkLayer_volt.json \
                > $out/share/vulkan/implicit_layer.d/VkLayer_volt.json

              # --- desktop entry + ícone ---
              mkdir -p $out/share/applications $out/share/icons/hicolor/256x256/apps
              cat > $out/share/applications/volt-gui.desktop <<EOF
              [Desktop Entry]
              Type=Application
              Version=1.0
              Name=volt-gui
              Comment=My AMD Adrenaline / NVIDIA Settings Linux Alternative
              Exec=volt-gui
              Icon=volt-gui
              Terminal=false
              Categories=Utility;
              Keywords=vulkan;vsync;gpu;gaming;
              StartupNotify=true
              StartupWMClass=volt-gui
              EOF
              cp $src/images/1.png $out/share/icons/hicolor/256x256/apps/volt-gui.png

              runHook postInstall
            '';

            meta = with pkgs.lib; {
              description = "Control panel for Vulkan games on Linux (RADV/ANV/NVK/AMDVLK/NVIDIA)";
              homepage = "https://github.com/pythonlover02/volt-gui";
              license = licenses.gpl3Only;
              platforms = [ "x86_64-linux" ];
              mainProgram = "volt-gui";
            };
          };
        };

        apps.default = {
          type = "app";
          program = "${self.packages.${system}.volt-gui}/bin/volt-gui";
        };

        devShells.default = pkgs.mkShell {
          inputsFrom = [ self.packages.${system}.volt-layer ];
          packages = with pkgs; [
            cargo rustc rustup gcc pkg-config
            python3Packages.pyside6
            vulkan-loader vulkan-validation-layers
          ];
        };

        # NixOS module: registra a layer no loader do sistema
        nixosModules.default = { config, lib, ... }: {
          options.programs.volt-gui.enable = lib.mkEnableOption "volt-gui Vulkan layer";
          config = lib.mkIf config.programs.volt-gui.enable {
            environment.systemPackages = [ self.packages.${system}.volt-gui ];
            environment.variables.VK_ADD_LAYER_PATH =
              "${self.packages.${system}.volt-gui}/share/vulkan/implicit_layer.d";
          };
        };
      });
}
