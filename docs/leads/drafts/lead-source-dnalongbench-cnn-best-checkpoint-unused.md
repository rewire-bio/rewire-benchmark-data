# CNN baseline: test score comes from the last epoch, not the saved best checkpoint

Raise at: https://github.com/ma-compbio/DNALONGBENCH (issues)  
Register entry: `lead-source-dnalongbench-cnn-best-checkpoint-unused`

In `experiments/CNN/train.py` at commit 6c43266c6dc85b5529b5a784b880ee88cc1a54b3, the `trainer` function saves the model whenever the validation score improves:

> `torch.save(model.state_dict(), os.path.join(save_dir, "best_model.pt"))`

After the epoch loop, the same function scores the test set with the model as it is in memory:

> `test_res = evaluate_model( args, model, test_loader, device, criterion, eval_metrics=evaluation_metric )`

No line in the script loads `best_model.pt` before that call, so the printed test score comes from the final epoch's weights rather than the best validation epoch.

Were the CNN figures in the paper produced with this script, and if so, should the test step load `best_model.pt` first? If the paper used a different selection, it would help to know which.

This was found while compiling an independent database of benchmark results: <record page>
