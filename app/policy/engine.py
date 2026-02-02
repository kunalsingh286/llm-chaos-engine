import yaml


class PolicyEngine:
    """
    Evaluates governance state and applies remediation
    """

    def __init__(
        self,
        actions,
        config_path="policies/policy_rules.yaml"
    ):

        self.actions = actions

        self.config_path = config_path

        self.policies = self._load()

    # -----------------------------

    def _load(self):

        with open(self.config_path, "r") as f:
            data = yaml.safe_load(f)

        return data.get("policies", [])

    # -----------------------------

    def evaluate(self, slo_state: dict):

        applied = []

        for policy in self.policies:

            name = policy["name"]

            condition = policy["condition"]

            actions = policy["actions"]

            if self._match(condition, slo_state):

                for action in actions:

                    self._execute(action)

                applied.append(name)

        return applied

    # -----------------------------

    def _match(self, condition, state):

        for key, val in condition.items():

            if state.get(key) != val:
                return False

        return True

    # -----------------------------

    def _execute(self, action_name):

        method = getattr(
            self.actions,
            action_name,
            None
        )

        if method:
            method()
