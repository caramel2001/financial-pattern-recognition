
import torch
import torch.nn as nn
import torch.optim.lr_scheduler as lr_scheduler
import pytorch_lightning as pl
from torch.utils.data import DataLoader

class TSFModel(pl.LightningModule):
    def __init__(self, model, lr):
        super().__init__()
        self.save_hyperparameters(ignore=["model"])

        self.model = model
        self.lr = lr

        self.loss_fn = torch.nn.MSELoss(reduction="mean")

    def forward(self, x):
        return self.model(x)

    def training_step(self, batch, batch_idx):
        X, y = batch
        preds = self(X)

        loss = self.loss_fn(preds, y)

        self.log("train_loss", loss)
        return loss

    def test_step(self, batch, batch_idx):
        X, y = batch
        preds = self(X)

        loss = self.loss_fn(preds, y)

        self.log("test_loss", loss)

    def predict_step(self, batch, batch_idx):
        X, _ = batch
        preds = self(X)
        return preds

    def configure_optimizers(self):
        opt = torch.optim.Adam(self.model.parameters(), lr=self.lr)
        scheduler = lr_scheduler.LinearLR(
            opt, start_factor=1.0, end_factor=0.5, total_iters=10
        )
        return [opt]

class TSFPredDataModule(pl.LightningDataModule):
    def __init__(self, X_pred, y_pred, batch_size, workers):
        super().__init__()
        self.batch_size = batch_size
        self.workers = workers
        self.X_pred = X_pred
        self.y_pred = y_pred

    def setup(self, stage=None):
        self.predset = torch.utils.data.TensorDataset(self.X_pred, self.y_pred)

    def predict_dataloader(self):
        return DataLoader(
            self.predset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.workers,
            pin_memory=False,
        )

class TSFDataModule(pl.LightningDataModule):
    def __init__(self, X_train, y_train, X_test, y_test, batch_size, workers):
        super().__init__()
        self.batch_size = batch_size
        self.workers = workers
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def setup(self, stage=None):
        self.trainset = torch.utils.data.TensorDataset(self.X_train, self.y_train)
        self.testset = torch.utils.data.TensorDataset(self.X_test, self.y_test)

    def train_dataloader(self):
        return DataLoader(
            self.trainset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.workers,
            pin_memory=True,
        )

    def test_dataloader(self):
        return DataLoader(
            self.testset,
            batch_size=self.batch_size,
            shuffle=True,
            num_workers=self.workers,
            pin_memory=False,
        )

    def predict_dataloader(self):
        return DataLoader(
            self.testset,
            batch_size=self.batch_size,
            shuffle=False,
            num_workers=self.workers,
            pin_memory=False,
        )