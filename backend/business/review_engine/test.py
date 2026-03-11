from agent.config_manager import Controller

class InterfaceAgent:
    def __init__(self, model = None):
        controller = Controller().review_config.get("LLM_CONFIG")
        if model is None:
            print(controller)
            model = controller.get("LLM_MODAL")

if __name__ == "__main__":
    controller = Controller().review_config.get("LLM_CONFIG")
    print(controller)
    model = controller.get("LLM_MODAL")
    print(model)