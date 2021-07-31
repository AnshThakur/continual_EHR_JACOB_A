from training import main
from data_processing import plot_demos

from pathlib import Path
from ray import tune

if __name__ == "__main__":
    # Specify dataset
    data='random'
    output_dir = Path(r'C:\Users\jacob\OneDrive\Documents\code\cl code\ehr')

    # Specify models
    models = ['MLP'] #,'CNN','RNN','LSTM']

    # Specify CL strategies
    strategies = ['Naive', 'Cumulative', 'Replay', 'SI', 'LwF', 'EWC']

    # Hyperparams for grid search
    config_generic = {'lr':tune.loguniform(1e-4, 1e-1), 
                      'optimizer':tune.choice(['SGD','Adam'])}

    # CL hyper-params: https://arxiv.org/pdf/2103.07492.pdf
    config_cl ={'Replay':{'mem_size':tune.choice([2,5,10])},
                'EWC':{'ewc_lambda':tune.loguniform(1e-3, 1e2)},
                'SI':{'si_lambda':tune.loguniform(1e-3, 1e2)},
                'LwF':{'alpha':tune.loguniform(1e-3, 1e2), 'temperature':tune.uniform(0,2)}}

    # Hyperparam opt over validation data for first 2 tasks
    main(data=data, output_dir=output_dir, models=models, strategies=strategies, config_generic=config_generic, config_cl=config_cl, validate=True)

    # Then train and test over all n>=2 tasks
    # Grab best params per model/strat
    # load config file
    # train normally (validate=False)
    # ...

    # Plotting
    if False:
        plot_demos()