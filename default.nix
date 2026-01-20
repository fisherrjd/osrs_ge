{ pkgs ? import
    (fetchTarball {
      name = "jpetrucciani-2026-01-19";
      url = "https://github.com/jpetrucciani/nix/archive/6518ae590ec45c2d128c07831442383728cde9ce.tar.gz";
      sha256 = "1qb153lpa7yzsykvmrmnypr2q4j8fn3gg0q6djhlaqdiwc96vq2h";
    })
    { }
}:
let
  name = "osrs_ge";

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
    db = [ duckdb ];
    bun = [ bun ];
    uv = [ uv uvEnv ];
    scripts = pkgs.lib.attrsets.attrValues scripts;
  };

  repo = "$(${pkgs.git}/bin/git rev-parse --show-toplevel)";

  scripts = with pkgs; {
    inherit (uvEnv.wrappers) black ruff ty;
    db = pkgs.pog {
      name = "db";
      script = ''
        ${uvEnv}/bin/python -m api.db.item_data
      '';
    };

    restart = pkgs.pog {
      name = "restart";
      script = ''
        ${pkgs.podman}/bin/podman pod rm -f osrs_ge-api
        ${pkgs.podman}/bin/podman play kube pod.yaml
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
  shellHook = ''
    repo="${repo}"
    export PYTHONPATH="$repo:$PYTHONPATH"
    export STREAMLIT_SERVER_ADDRESS=0.0.0.0
    ln -sf ${uvEnv.uvEnvVars._UV_SITE} .direnv/site
  '';
} // uvEnv.uvEnvVars)) // { inherit scripts; }
