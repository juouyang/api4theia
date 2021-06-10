rm -rf ${PWD}/Doquant/Strategy
mkdir -p ${PWD}/Doquant/Strategy
cd ${PWD}/Doquant/Strategy
ssh-agent bash -c 'ssh-add ../../github_key_doquant; git clone --depth 1 git@github.com:ian15937/Doquant.git .; git filter-branch --prune-empty --subdirectory-filter Strategy HEAD'