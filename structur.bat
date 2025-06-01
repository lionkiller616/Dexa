@echo off
echo Creating Daxa project structure...

REM Root folders
md assets\icons
md daxa\cli\commands
md daxa\core
md daxa\dxd
md daxa\maths
md daxa\config
md daxa\data_lang
md daxa\document
md daxa\gui\dialogs
md daxa\gui\widgets
md daxa\utils
md examples
md tests

REM Assets
echo. > assets\daxa_style_dark.qss
echo. > assets\daxa_style_light.qss
echo. > assets\icon.ico
echo. > assets\icon.png
echo. > assets\logo.png
echo. > assets\icons\open.svg
echo. > assets\icons\save.svg
echo. > assets\icons\settings.svg
echo. > assets\icons\validate.svg
echo. > assets\icons\render_html.svg
echo. > assets\icons\dxd_icon.svg
echo. > assets\icons\math_icon.svg
echo. > assets\icons\config_icon.svg
echo. > assets\icons\data_icon.svg
echo. > assets\icons\type_icon.svg
echo. > assets\icons\cut.svg
echo. > assets\icons\copy.svg
echo. > assets\icons\paste.svg
echo. > assets\icons\zoom.svg

REM Top-level Daxa
echo. > daxa\__init__.py

REM CLI
echo. > daxa\cli\__init__.py
echo. > daxa\cli\main.py
echo. > daxa\cli\commands\__init__.py
echo. > daxa\cli\commands\base_command.py
echo. > daxa\cli\commands\convert_cmd.py
echo. > daxa\cli\commands\dxd_cmd.py
echo. > daxa\cli\commands\info_cmd.py
echo. > daxa\cli\commands\init_cmd.py
echo. > daxa\cli\commands\math_cmd.py
echo. > daxa\cli\commands\render_cmd.py
echo. > daxa\cli\commands\validate_cmd.py

REM Core
echo. > daxa\core\__init__.py
echo. > daxa\core\common.py
echo. > daxa\core\daxa_value.py
echo. > daxa\core\parser_main.py
echo. > daxa\core\schema.py
echo. > daxa\core\validator.py
echo. > daxa\core\writer_main.py
echo. > daxa\core\parser_binary.py
echo. > daxa\core\writer_binary.py

REM DXD
echo. > daxa\dxd\__init__.py
echo. > daxa\dxd\dxd_ast.py
echo. > daxa\dxd\dxd_parser.py
echo. > daxa\dxd\dxd_renderer_svg.py
echo. > daxa\dxd\dxd_renderer_png.py

REM Maths
echo. > daxa\maths\__init__.py
echo. > daxa\maths\maths_ast.py
echo. > daxa\maths\maths_parser.py
echo. > daxa\maths\maths_renderer_svg.py

REM Config
echo. > daxa\config\__init__.py
echo. > daxa\config\dxc_ast.py
echo. > daxa\config\dxc_parser.py
echo. > daxa\config\dxc_evaluator.py

REM Data Language
echo. > daxa\data_lang\__init__.py
echo. > daxa\data_lang\dx_model.py
echo. > daxa\data_lang\dx_parser.py
echo. > daxa\data_lang\dx_query_engine.py

REM Document
echo. > daxa\document\__init__.py
echo. > daxa\document\doc_model.py
echo. > daxa\document\prose_parser.py
echo. > daxa\document\doc_renderer_html.py
echo. > daxa\document\doc_renderer_pdf.py

REM GUI
echo. > daxa\gui\__init__.py
echo. > daxa\gui\main_window.py
echo. > daxa\gui\resources.py
echo. > daxa\gui\style.py
echo. > daxa\gui\threads.py
echo. > daxa\gui\view_model.py
echo. > daxa\gui\dialogs\__init__.py
echo. > daxa\gui\dialogs\error_dialog.py
echo. > daxa\gui\dialogs\preferences_dialog.py
echo. > daxa\gui\widgets\__init__.py
echo. > daxa\gui\widgets\console_widget.py
echo. > daxa\gui\widgets\daxa_editor_widget.py
echo. > daxa\gui\widgets\daxa_preview_widget.py
echo. > daxa\gui\widgets\outline_widget.py
echo. > daxa\gui\widgets\property_editor.py

REM Utils
echo. > daxa\utils\__init__.py
echo. > daxa\utils\compression.py
echo. > daxa\utils\db_utils.py
echo. > daxa\utils\encryption.py
echo. > daxa\utils\misc_utils.py
echo. > daxa\daxa_settings.py

REM Examples
echo. > examples\main_document.daxa
echo. > examples\my_app_config.dxc
echo. > examples\product_catalog.dx
echo. > examples\simple_flowchart.dxd
echo. > examples\complex_equations.maths
echo. > examples\old_person_data.daxa

REM Tests
echo. > tests\__init__.py
echo. > tests\conftest.py
echo. > tests\test_cli_commands.py
echo. > tests\test_core_parser_main.py
echo. > tests\test_core_schema.py
echo. > tests\test_core_daxa_value.py
echo. > tests\test_core_validator.py
echo. > tests\test_dxd_parser.py
echo. > tests\test_dxd_renderer_svg.py
echo. > tests\test_maths_parser.py
echo. > tests\test_maths_renderer_svg.py
echo. > tests\test_dxc_parser.py
echo. > tests\test_dx_data_parser.py
echo. > tests\test_doc_model.py
echo. > tests\test_doc_renderer_html.py

REM Root files
echo. > .gitignore
echo MIT License > LICENSE
echo # Daxa System > README.md
echo PyQt6 > requirements.txt
echo from setuptools import setup > setup.py

echo.
echo All done!
pause
