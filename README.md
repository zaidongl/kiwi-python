# kiwi-python
Common reusable BDD test automation framework in python

## Features
- BDD with `behave`
- Support Web test automation with `playwright`
- Support reporting with `allure`
- To add...

## How to run
1. Clone the repository
    ```bash
    git clone
    ```
2. Install dependencies
    ```bash
    pip install -r requirements.txt
    ```

3. Run web application https://github.com/cypress-io/cypress-realworld-app on local following its readme instructions.

4. Run tests
   Go to folder ./examples/real_world_reg_tests and run:
    ```bash
    behave .
    ```

5. Generate and view Allure report
   ```bash
   allure generate --clean
   ```
    ```bash
    allure serve allure-report/
    ```
