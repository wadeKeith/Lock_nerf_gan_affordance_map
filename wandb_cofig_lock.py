import math
# import wandb

# 超参数搜索方法，可以选择：grid random bayes
sweep_config = {
    'method': 'random',
    "name": "lock_sweep",
    "metric": {"goal": "minimize", "name": "total_loss"}
    }

# 参数范围
parameters_dict = {
    'fov': {
        # a flat distribution between 0 and 0.1
        'distribution': 'uniform',
        'min': 10,
        'max': 60
      },
    'ray_start':{
        'value':0.7
        },
    'ray_end':{
        'value':1.3
        },
    'fade_steps': {
          'values': [10000, 5000, 20000]
        },
    'sample_dist': {
          'value': 'lock'
        },
    'h_stddev': {
          'value': math.pi/3
        },
    'v_stddev': {
          'value': math.pi/4 * 85/90
        },
    'h_mean': {
          'value': 0
        },
    'v_mean': {
          'value': math.pi/4 * 85/90
        },
    'topk_interval': {
        'values': [1000, 2000, 3000]
      },
    'topk_v': {
        # a flat distribution between 0 and 0.1
        'distribution': 'uniform',
        'min': 0.1,
        'max': 1
      },
    'betas': {
          'values': [(0, 0.9),(0.2,0.9), (0.3,0.9), (0.4,0.9), (0.5,0.9), (0.6,0.9), (0.7,0.9),(0.8,0.9), (0.9,0.999)]
        },
    'unique_lr':{
        'values': [False, True]
        },
    'weight_decay': {
        # a flat distribution between 0 and 0.1
        'distribution': 'uniform',
        'min': 0,
        'max': 0.1
      },
    'r1_lambda': {
        # a flat distribution between 0 and 0.1
        'distribution': 'uniform',
        'min': 0.1,
        'max': 20
      },
    'latent_dim':{
        'values':[256, 512, 1024]
        },
    'grad_clip': {
        # a flat distribution between 0 and 0.1
        'distribution': 'uniform',
        'min': 1,
        'max': 10
      },
    'model': {
          'value': 'TALLSIREN'
        },
    'generator': {
          'value': 'ImplicitGenerator3d'
        },
    'discriminator': {
          'value': 'ProgressiveEncoderDiscriminator'
        },
    'dataset': {
          'value': 'lock'
        },
    'white_back': {
        'values': [False, True]
      },
    'clamp_mode': {
        'values': ['relu', 'softplus']
      },
    'z_dist': {
        'values': ['gaussian', 'uniform']
        },
    'hierarchical_sample': {
          'value': True
        },
    'z_lambda': {
          'value': 0
        },
    'learnable_dist': {
        'values': [False, True]
      },

    # 'batch_size': {
    #     # integers between 32 and 256
    #     # with evenly-distributed logarithms 
    #     'distribution': 'q_log_uniform',
    #     'q': 1,
    #     'min': math.log(32),
    #     'max': math.log(256),
    #   }
    }

sweep_config['parameters'] = parameters_dict

# wandb.agent()