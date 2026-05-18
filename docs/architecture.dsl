workspace "Bank Churn Prediction" {
    model {
        user = person "Bank Staff" "Uses the system to predict churn."
        system = softwareSystem "Churn Prediction Platform" "Predicts customer churn using ML." {
            db = container "Database" "Stores customer data" "SQLite"
            mlServer = container "ML Server" "Runs models" "Python Flask/FastAPI" {
                dataPipeline = component "Data Pipeline" "Preprocesses data"
                predictor = component "Predictor" "Runs ML model"
                visualizer = component "Visualizer" "Generates explanations (SHAP)"
                dataPipeline -> predictor "Feeds processed data"
                predictor -> visualizer "Sends results"
            }
            ui = container "Web UI" "User interface" "HTML/JS/Streamlit"
            user -> ui "Interacts with"
            ui -> mlServer "Calls API"
            mlServer -> db "Queries data"
        }
        user -> system "Accesses predictions"
    }

    views {
        systemContext system "ContextView" "Overall system context." {
            include *
            autoLayout
        }
        container system "ContainerView" "High-level containers." {
            include *
            autoLayout
        }
        component mlServer "ComponentView" "ML Server components." {
            include *
            autoLayout
        }
        theme Default
    }
}
