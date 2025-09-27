{
  description = "Automatically enable ASPM on all supported PCIe devices";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs-unstable";
  };

  outputs =
    {
      self,
      nixpkgs,
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
      ];
      forAllSystems =
        f:
        nixpkgs.lib.genAttrs systems (
          system:
          f rec {
            pkgs = nixpkgs.legacyPackages.${system};
            commonPackages = builtins.attrValues {
              inherit (pkgs.python3Packages)
                python
                ;
            };
          }
        );
    in
    {
      devShells = forAllSystems (
        {
          pkgs,
          commonPackages,
          pciutils,
        }:
        {
          default = pkgs.mkShell {
            packages = commonPackages;
          };
        }
      );
      nixosModules.default =
        {
          config,
          pkgs,
          lib,
        }:
        let
          cfg = config.services.auto-aspm;
        in
        {
          options.services.auto-aspm = {
            enable = lib.mkEnableOption "Automatically activate ASPM on all supported devices";
          };

          config = lib.mkIf cfg.enable {
            environment.systemPackages = [
              pkgs.autoaspm
            ];
            systemd.services.auto-aspm = {
              description = "Automatically activate ASPM on all supported devices";
              wantedBy = [ "multi-user.target" ];
              path = [
                pkgs.python313
                pkgs.which
                pkgs.pciutils
                pkgs.autoaspm
              ];
              serviceConfig = {
                Type = "oneshot";
                ExecStart = "${lib.getExe pkgs.python313} ${lib.getExe pkgs.autoaspm}";
              };
            };
          };
        };
      packages = forAllSystems (
        {
          pkgs,
          commonPackages,
        }:
        {
          default = pkgs.python3Packages.buildPythonApplication {
            name = "autoaspm";
            pname = "autoaspm";
            format = "pyproject";
            src = ./.;
            propagatedBuildInputs = commonPackages;
            meta = {
              description = "";
              homepage = "https://github.com/notthebee/autoaspm";
              license = pkgs.lib.licenses.mit;
              maintainers = [ "notthebee" ];
              platforms = systems;
            };
          };
        }
      );
    };
}
