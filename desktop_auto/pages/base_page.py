from desktop_auto.config import AutomationConfig


class BasePage:
    def __init__(self, driver, config: AutomationConfig):
        self.driver = driver
        self.config = config

    def find_by_selector_name(self, selector_name: str):
        return self.find_by_accessibility_token(self.config.selector(selector_name))

    def find_by_accessibility_token(self, token: str):
        last_error = None
        for strategy, value in self._locator_candidates(token):
            try:
                return self.driver.find_element(strategy, value)
            except Exception as error:
                last_error = error
        raise last_error

    def click(self, selector_name: str) -> None:
        self.find_by_selector_name(selector_name).click()

    def find_optional_by_selector_name(self, selector_name: str):
        try:
            return self.find_by_selector_name(selector_name)
        except Exception:
            return None

    def _locator_candidates(self, selector: str):
        return [
            ("accessibility id", selector),
            ("name", selector),
            (
                "-ios predicate string",
                f"identifier == '{selector}' OR identifier ENDSWITH '.{selector}' OR identifier CONTAINS '.{selector}.'",
            ),
        ]
