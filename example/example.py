from experiment_automator.experiment_automator import ExperimentAutomator

if __name__ == "__main__":
    ExperimentAutomator("config.yml").run(lambda automator, attrs: {
        # Write your logic to here !!! :)

        # Return your results
        "name": "mutlu", "surname": "polatcan", "age": 24
    })
