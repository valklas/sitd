{
    description = "SITD Development Environment";

    inputs = {
        nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    };

    outputs = { self, nixpkgs }:
        let
        system = "x86_64-linux";
    pkgs = import nixpkgs {
        inherit system;
    };
    in {
        devShells.${system}.default = pkgs.mkShell {
            packages = with pkgs; [
                python3
                bun
                fish
                git
            ];

            shellHook = ''
                exec fish
            ''
        };
    };
}
