# Testing with `pytest`

Similar to `pylint`, the `pytest` command can be injected into the venv `pipx` created for the `standardebooks` package:

```shell
pipx inject standardebooks pytest==8.3.4
```

The tests are executed by calling `pytest` from the top level of your tools repo:

```shell
cd /path/to/tools/repo
$HOME/.local/pipx/venvs/standardebooks/bin/pytest
```

## Test structure

Testing is structured such that, for most testing, all that is needed to implement a new test is to create a directory structure and a set of input files.

Tests are located in the `tests` subdirectory of the `tools` top-level directory. The various `se` commands have been divided into modules based on what they take as input and deliver as output. There is a module code file (`test_{module}.py`) and a directory for each module. Each module code file contains documentation that lists the `se` commands that are included in that module.

The modules are:

1. `build_command`—This module is for testing the `se build` command. It takes a feature-complete SE ebook directory structure as input, combined with optional file(s) provided for the test, and performs two steps: first, it builds the ebook, then, if one is created, it extracts the compatibility epub file generated by the build.

2. `draft_commands`—These take a draft (i.e. incomplete) SE ebook directory structure as input, combined with the file(s) provided for the test, and update one or more of the ebook files in some way. Each command has its own subdirectory, and each test for the command is in a subdirectory beneath that one. The tests are named test-X, e.g. test-1, test-2, test-13, etc. There are some special cases within this module:

    * The `build-loi`, `build-manifest`, `build-spine`, `build-title`, and `build-toc` commands can all either update file(s) in the ebook structure, or output to stdout. These commands can thus be tested as part of both this module (when updating files) or the `stdout_commands` module, when writing their output to stdout. When testing within this module, therefore, tests for these commands, if they have command files (see `Creating a test` below), cannot include the `--stdout` argument.

3. `ebook_commands`—These take a feature-complete SE ebook directory structure as input, combined with the file(s) provided for the test, and update one or more of the files. The test directory structure is the same as for draft_commands.

4. `file_commands`—These take one file as input, or in the case of create-draft, nothing, and produce files (possibly in a directory tree) as output. The test directory structure is the same as for draft_commands, but the `in` directory only contains a single file, or, in the case of `create-draft`, is not needed.

5. `stdout_commands`—These take a draft (i.e. incomplete) SE ebook directory structure as input, combined with the file(s) provided for the test, and output text to stdout. The test directory structure is the same as for draft_commands. There are two sets of special cases within this module:

    * The `build-loi`, `build-manifest`, `build-spine`, `build-title`, and `build-toc` commands can all either update file(s) in the ebook structure, or output to stdout. These commands can thus be tested as part of both the `draft_commands` module (when updating files) or this module, when writing their output to stdout. If there is no command-file, then the `--stdout` argument is added automatically. If any tests for these commands have a command file, that command file must contain at least the command and the `--stdout` argument.
  
    * The `unicode-names` and `help` commands do not take ebook files as input, and therefore do not need an `in` directory. The `unicode-names` command takes a string as input, and therefore all tests require a command file with the command and the string to use as input. The `help` command does not take any input at all.

6. `lint`—`se`’s lint command takes a feature-complete ebook directory structure as input, combined with the file(s) provided for the test, and writes any errors found in the result to stdout. There is a separate directory for each type of lint error, e.g. `css`, `filesystem`, `metadata`, etc. Each of those directories contain the test directories for the errors of that type. The test directories are named for the specific lint error being tested, e.g. `c-003`, `x-015`, etc. Each error has a single test, and therefore a single directory.

7. `string_commands`—These take a string as input and output a string to stdout. Since they do not take file input, all tests are contained in a single file named for the command being tested. The file contains one comma-delimited line per test, with the input before the comma and the expected output after.

8. In addition, there is a `data` directory that contains two SE ebook structures beneath it, one for a draft ebook (created via `se create-draft`) used by the `draft_commands` and `stdout_commands` modules, and one for a feature-complete test ebook, i.e. it builds without error and generates no lint errors, used by the `build`, `ebook_commands` and `lint` modules.

## Creating a test

For the first five modules above (build, draft, ebook, file, stdout), creating a test involves these steps.

1. If the subdirectory for the command being tested does not exist below the module directory, create it; the subdirectory name is the same as the command name.

2. Create a subdirectory beneath the command directory labeled `test-X`, where X is the next test number in sequence. For example, if `test-1` through `test-5` already exists, then create a `test-6` directory.

3. Within that new test directory, create `golden` and `in` subdirectories. As noted above, there are a few commands that do not require or do not use the `in` subdirectory, e.g. the `build` command can have input files but do not require them, and the `create-draft` command does not take any input and therefore does not need an `in` subdirectory.

4. Within the `in` directory, create the minimum SE ebook directory tree needed for the file(s) being used in the test. For example, if only a chapter file is needed for the test, then create an `src/epub/text` directory structure. If a css file is needed for the test, create a `src/epub/css` directory structure. And so forth.

5. Copy/create the file(s) needed for the test into that directory structure, putting the file(s) in the appropriate directory(ies).

6. If no arguments are necessary for the `se` command being tested, that is all that is needed in the `text-X` directory. However, if arguments are needed for the test, then a file named `{command}-command`, e.g. `build-manifest-command`, should be created in the test directory. That file should contain a single line, with the command name and arguments on it. Thus, to test that the standard out argument to the `build-manifest` command is working, create a `build-manifest-command` file in the `test-X` directory and populate it with a line containing `build-manifest --stdout`.

7. Run the new test (and _only_ the new test) with the `--save-golden-files` option to create valid “golden” file(s) for the test, i.e. the files that future tests will be compared against. See Running tests below for how to run a single test. After creating the golden files, review them to ensure that the output is valid, i.e. that the command produced the file changes that were expected.

For lint, the steps are almost the same, with the exception of the top-level test directory.

1. Beneath the appropriate lint subtype directory, create a directory for the lint error id being tested. For example, c-XXX errors are beneath the `css` directory, m-XXX errors beneath the `metadata` directory, etc. Note that unlike the above modules, there should only be a single test for each lint error id. If additional conditions need to be tested for a lint error, the existing input file(s) should be updated to include the additional conditions.

2. Continue the above steps, beginning with step #3.

3. A lint test should be thorough; if the lint error has exceptions, those exceptions should be included as part of the test. If the lint error has multiple matches, each match should be tested. E.g., see the `y-003` test input files.

    In addition, each test should try to restrict the errors generated to just the individual lint error being tested. If that is impossible, please note in the input files that the additional error will be generated for that condition. See again the `y-003` test input files.

For string commands:

1. Each string command already has a file, with the same name as the command, containing one or more tests.

2. To add additional tests, or modify existing ones, edit the existing command file and add additional lines at the bottom of the file for the additional test(s).

3. Each line in the file consists of: the input to the command, a comma, and the “golden” output from the command.

## Running tests

To run all tests manually, run `pytest tests` from the top-level `tools` directory.

To run a single module's test, include the module filename, e.g. `pytest tests/test_stdout_commands.py`.

To run a single test, include the module file basename and the test id in the format `pytest tests/test_{module}.py::test_{module}[{test-id}]`. For example, the third test for `word-count` would be `pytest tests/test_stdout_commands.py::test_stdout_commands[word-count-test-3]`.

For lint, the format is `tests_lint.py::test_lint[{lint-subtype}-{lint-error-id}]`, e.g. `pytest tests/test_lint.py::test_lint[css-c-003]`.

To see test ids, run pytest in collect-only mode, e.g. `pytest --collect-only tests` or `pytest --collect-only tests:/test_lint.py`, or pass the -v[v] option when running the tests, e.g. `pytest -v tests`.

The testing directory structure:
```
|__ tests/
|   |__ conftest.py—pytest configuration file
|   |__ helpers.py—pytest helper fixtures, etc.
|   |__ test_build_command.py
|   |__ test_draft_commands.py
|   |__ test_ebook_commands.py
|   |__ test_file_commands.py
|   |__ test_internals.py
|   |__ test_lint.py
|   |__ test_stdout_commands.py
|   |__ test_string_commands.py
|
|__ data/
|   |__ draftbook/
|   |   |__ a complete draft ebook structure
|   |
|   |__ testbook/
|   |   |__ a feature-complete test ebook structure
|
|__ build/
|   |   |__ test-1/
|   |   |   |__ golden/
|   |   |   |__ in/
|   |__ etc.
|
|__ draft_commands/
|   |__ british2american/
|   |   |   |__ test-1/
|   |   |   |   |__ golden/
|   |   |   |   |__ in/
|   |__ build-loi/
|   |   |   |__ test-1/
|   |   |   |   |__ golden/
|   |   |   |   |__ in/
|   |   |   |__ test-2/
|   |   |   |   |__ golden/
|   |   |   |   |__ in/
|   |__ etc.
|
|__ ebook_commands/
|   |__ build-ids/
|   |   |   |__ test-1/
|   |   |   |   |__ golden/
|   |   |   |   |__ in/
|   |__ etc.
|
|__ file_commands/
|   |__ create-draft/
|   |   |   |__ test-1/
|   |   |   |   |__ golden/
|__ . . .
|   |__ split-file/
|   |   |   |__ test-1/
|   |   |   |   |__ golden/
|   |   |   |   |__ in/
|   |__ etc.
|
|__ lint/
|   |__ css/
|   |   |__ c-001/
|   |   |   |__ golden/
|   |   |   |   |__ c-001-out.txt
|   |   |   |__ in/
|__ . . .
|   |__ filesystem/
|   |   |__ f-001/
|   |   |   |__ golden/
|   |   |   |   |__ f-001-out.txt
|   |   |   |__ in/
|   |__ etc.
|
|__ stdout_commands/
|   |__ build-loi/
|   |   |   |__ test-1/
|   |   |   |   |__ golden/
|   |   |   |   |__ in/
|__ . . .
|   |__ css-select/
|   |   |   |__ test-1/
|   |   |   |   |__ golden/
|   |   |   |   |__ in/
|   |__ etc.
|
|__ string_commands/
|   |__ dec2roman
|   |__ make-url-safe
|   |__ roman2dec
|   |__ titlecase
````
