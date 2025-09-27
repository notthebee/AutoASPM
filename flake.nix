{
  description = "Automatically enable ASPM on all supported PCIe devices";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";
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
      eachSystem = nixpkgs.lib.genAttrs systems;
    in
    {
      devShells = eachSystem (
        system:
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
      nixosModules.auto-aspm = ./modules/autoaspm.nix;
      nixosModules.default = self.nixosModules.auto-aspm;
      packages = eachSystem (system: {
        default = self.packages.${system}.autoaspm;
        autoaspm = nixpkgs.legacyPackages.${system}.callPackage ./pkgs/autoaspm.nix { };
      });
    };
}
