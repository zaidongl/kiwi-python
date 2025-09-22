@home-page
Feature: Home Page is loaded after login
    As a user
    I want to verify that the home page is loaded after login

    Scenario: login with valid credentials
        When "BrowserAgent" opens the page "/"
        Then "BrowserAgent" is on "Login-Page"
        When "BrowserAgent" type "test-user" into "Login-Page.user-textbox" and "test" into "Login-Page.password-textbox"
        Then "BrowserAgent" clicks "Login-Page.signin-button"
        Then "BrowserAgent" is on "Home-Page"
