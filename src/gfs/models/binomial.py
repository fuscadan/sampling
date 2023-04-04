from gfs.models.model import Model
from gfs.sample.bayes import Likelihood, Prior
from gfs.sample.domain import Axis, Domain
from gfs.sample.elements import DataPoint, Distribution, Parameter, XDataPoint
from gfs.sample.functions import constant, linear
from gfs.sample.leaf import LeafList


class BinomialLikelihood(Likelihood):
    def __init__(self, domain: Domain):
        super().__init__(domain=domain)

    def __repr__(self) -> str:
        return f"BinomialLikelihood(bit_depth={self.domain.bit_depth})"

    def leaves(self, datum: DataPoint) -> LeafList:
        trial_result = datum.y
        if trial_result == 0:
            return linear(domain_bit_depth=self.domain.bit_depth, reverse=True)
        if trial_result == 1:
            return linear(domain_bit_depth=self.domain.bit_depth, reverse=False)

        raise ValueError(f"Invalid datum: {datum}")


class BinomialModel(Model):
    def __init__(self, bit_depth: int):
        param_axis = Axis(
            name="bias_towards_heads",
            left_endpoint=0.0,
            right_endpoint=1.0,
            bit_depth=bit_depth,
        )
        param_domain = Domain([param_axis])
        super().__init__(
            param_domain=param_domain,
            prior=Prior(constant(domain_bit_depths=[param_domain.bit_depth])),
            likelihood=BinomialLikelihood(domain=param_domain),
            categories=("tails", "heads"),
        )

    def dist(self, param: Parameter, x: XDataPoint | None) -> Distribution:
        bias_towards_heads = param[0]
        return Distribution([1 - bias_towards_heads, bias_towards_heads])
