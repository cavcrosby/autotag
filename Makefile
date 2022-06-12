include base.mk

# include other generic makefiles
include python.mk
# overrides defaults set by included makefiles
VIRTUALENV_PYTHON_VERSION = 3.9.5
PYTHON_VIRTUALENV_NAME = $(shell basename ${CURDIR})

# simply expanded variables
executables := \
	${python_executables}

_check_executables := $(foreach exec,${executables},$(if $(shell command -v ${exec}),pass,$(error "No ${exec} in PATH")))

.PHONY: ${HELP}
${HELP}:
	# inspired by the makefiles of the Linux kernel and Mercurial
>	@echo 'Common make targets:'
>	@echo '  ${SETUP}          - creates and configures the virtualenv to be used'
>	@echo '                   by the project, also useful for development'

.PHONY: ${SETUP}
${SETUP}: ${PYENV_POETRY_SETUP}
