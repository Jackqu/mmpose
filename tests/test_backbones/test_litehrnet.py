import torch
from torch.nn.modules.batchnorm import _BatchNorm

from mmpose.models.backbones import LiteHRNet
from mmpose.models.backbones.resnet import Bottleneck


def is_norm(modules):
    """Check if is one of the norms."""
    if isinstance(modules, (_BatchNorm, )):
        return True
    return False


def all_zeros(modules):
    """Check if the weight(and bias) is all zero."""
    weight_zero = torch.equal(modules.weight.data,
                              torch.zeros_like(modules.weight.data))
    if hasattr(modules, 'bias'):
        bias_zero = torch.equal(modules.bias.data,
                                torch.zeros_like(modules.bias.data))
    else:
        bias_zero = True

    return weight_zero and bias_zero


def test_litehrnet_backbone():
    extra = dict(
        stem=dict(stem_channels=32, out_channels=32, expand_ratio=1),
        num_stages=3,
        stages_spec=dict(
            num_modules=(2, 4, 2),
            num_branches=(2, 3, 4),
            num_blocks=(2, 2, 2),
            module_type=('LITE', 'LITE', 'LITE'),
            with_fuse=(True, True, True),
            reduce_ratios=(8, 8, 8),
            num_channels=(
                (40, 80),
                (40, 80, 160),
                (40, 80, 160, 320),
            )),
        with_head=True)

    model = LiteHRNet(extra, in_channels=3)

    imgs = torch.randn(2, 3, 224, 224)
    feat = model(imgs)
    assert len(feat) == 1
    assert feat[0].shape == torch.Size([2, 40, 56, 56])

    # Test HRNet zero initialization of residual
    model = LiteHRNet(extra, in_channels=3, zero_init_residual=True)
    model.init_weights()
    for m in model.modules():
        if isinstance(m, Bottleneck):
            assert all_zeros(m.norm3)
    model.train()

    imgs = torch.randn(2, 3, 224, 224)
    feat = model(imgs)
    assert len(feat) == 1
    assert feat[0].shape == torch.Size([2, 40, 56, 56])