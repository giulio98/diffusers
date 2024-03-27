import torch.nn as nn

from ...attention import BasicTransformerBlock
from ...embeddings import ImagePositionalEmbeddings
from ..transformer_2d import Transformer2DModel


class VectorizedTransformer2DModel(Transformer2DModel):
    def __init__(
        self,
        in_channels,
        sample_size,
        num_vector_embeds,
        inner_dim,
        num_attention_heads,
        attention_head_dim,
        dropout,
        cross_attention_dim,
        activation_fn,
        num_embeds_ada_norm,
        attention_bias,
        only_cross_attention,
        double_self_attention,
        upcast_attention,
        norm_type,
        norm_elementwise_affine,
        norm_eps,
        attention_type,
        num_layers,
    ):
        super().__init__(
            num_attention_heads=num_attention_heads,
            attention_head_dim=attention_head_dim,
            in_channels=in_channels,
            num_layers=num_layers,
            dropout=dropout,
            cross_attention_dim=cross_attention_dim,
            attention_bias=attention_bias,
            sample_size=sample_size,
            num_vector_embeds=num_vector_embeds,
            activation_fn=activation_fn,
            num_embeds_ada_norm=num_embeds_ada_norm,
            only_cross_attention=only_cross_attention,
            double_self_attention=double_self_attention,
            upcast_attention=upcast_attention,
            norm_type=norm_type,
            norm_elementwise_affine=norm_elementwise_affine,
            norm_eps=norm_eps,
            attention_typ=attention_type,
        )

        self.in_channels = in_channels

        assert sample_size is not None, "Transformer2DModel over discrete input must provide sample_size"
        assert num_vector_embeds is not None, "Transformer2DModel over discrete input must provide num_embed"

        self.height = sample_size
        self.width = sample_size
        self.num_vector_embeds = num_vector_embeds
        self.num_latent_pixels = self.height * self.width

        self.latent_image_embedding = ImagePositionalEmbeddings(
            num_embed=num_vector_embeds, embed_dim=inner_dim, height=self.height, width=self.width
        )

        self.transformer_blocks = nn.ModuleList(
            [
                BasicTransformerBlock(
                    inner_dim,
                    num_attention_heads,
                    attention_head_dim,
                    dropout=dropout,
                    cross_attention_dim=cross_attention_dim,
                    activation_fn=activation_fn,
                    num_embeds_ada_norm=num_embeds_ada_norm,
                    attention_bias=attention_bias,
                    only_cross_attention=only_cross_attention,
                    double_self_attention=double_self_attention,
                    upcast_attention=upcast_attention,
                    norm_type=norm_type,
                    norm_elementwise_affine=norm_elementwise_affine,
                    norm_eps=norm_eps,
                    attention_type=attention_type,
                )
                for d in range(num_layers)
            ]
        )

        self.norm_out = nn.LayerNorm(inner_dim)
        self.out = nn.Linear(inner_dim, self.num_vector_embeds - 1)
