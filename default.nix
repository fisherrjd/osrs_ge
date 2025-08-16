{ pkgs ? import
    (fetchTarball {
      name = "jpetrucciani-2025-08-15";
      url = "https://github.com/jpetrucciani/nix/archive/62e6f6f1a1056ef49430dd1118bb602c59417d5c.tar.gz";
      sha256 = "1sdcgcxy8id80z41ri16988yrhndam6nbq6d1rbr035wnlw3rwl1";
    })
    { }
}:
let
  name = "osrsGE";

  uvEnv = pkgs.uv-nix.mkEnv {
    inherit name; python = pkgs.python313;
    workspaceRoot = pkgs.hax.filterSrc { path = ./.; };
    pyprojectOverrides = final: prev: { };
  };

  tools = with pkgs; {
    cli = [
      jfmt
      nixup
    ];
    uv = [ uv uvEnv ];
    scripts = pkgs.lib.attrsets.attrValues scripts;
  };

  scripts = with pkgs; {
    db = pkgs.pog {
      name = "db";
      script = ''
        ${uvEnv}/bin/python -m db.data_input
      '';
    };
  };
  paths = pkgs.lib.flatten [ (builtins.attrValues tools) ];
  env = pkgs.buildEnv {
    inherit name paths; buildInputs = paths;
  };
in
(env.overrideAttrs (_: {
  inherit name;
  NIXUP = "0.0.9";
} // uvEnv.uvEnvVars)) // { inherit scripts; }
