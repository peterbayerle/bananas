# helpers
doesnt_have_param() {
    local term="$1"
    shift
    for arg; do
        if [[ $arg == "$term" ]]; then
            return 1
        fi
    done
    return 0
}

# install requirements for preprocessing
if doesnt_have_param '-si' "$@"; then
  python3 -m venv scripts/venv
  . scripts/venv/bin/activate
  python3 -m pip install --upgrade pip
  python3 -m pip install -r scripts/requirements.txt
else
  . scripts/venv/bin/activate
fi

# run tests and preprocess NASPA data
if doesnt_have_param '-sp' "$@"; then
  python3 scripts/test_preprocess_naspa.py
  if (exit $?)
  then
      echo "Tests passed, preprocessing NASPA dictionaries now ..."
  else
      echo "Tests fail for preprocessing"
      exit 1
  fi
  python3 scripts/preprocess_naspa_dicts.py
fi

# create tables and populate with preprocessed data
if doesnt_have_param '-st' "$@"; then
  python3 scripts/create_tables.py
fi
