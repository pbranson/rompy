"""Subcomponents to be rendered inside of components."""
import logging
from typing import Optional, Literal
from pydantic import root_validator, confloat, constr, conint

from rompy.swan.subcomponents.base import BaseSubComponent


logger = logging.getLogger(__name__)


class SIDE(BaseSubComponent):
    """SWAN SIDE BOUNDSPEC subcomponent.

    `SIDE NORTH|NW|WEST|SW|SOUTH|SE|E|NE CCW|CLOCKWISE`

    The boundary is one full side of the computational grid (in 1D cases either of the
    two ends of the 1D-grid). SHOULD NOT BE USED IN CASE OF CURVILINEAR GRIDS!

    Parameters
    ----------
    model_type: Literal["side"]
        Model type discriminator.
    side: Literal["north", "nw", "west", "sw", "south", "se", "east", "ne"]
        The side of the grid to apply the boundary to.

    """

    model_type: Literal["side"] = "side"
    side: Literal["north", "nw", "west", "sw", "south", "se", "east", "ne"]
    direction: Literal["ccw", "clockwise"] = "ccw"

    def cmd(self) -> str:
        repr = f"SIDE {self.side.upper()} {self.direction.upper()} "
        return repr


class SEGMENTXY(BaseSubComponent):
    """SWAN SEGMENT XY BOUNDSPEC subcomponent.

    `SEGMENT XY < [x] [y] >`

    The segment is defined by means of a series of points in terms of problem
    coordinates; these points do not have to coincide with grid points. The (straight)
    line connecting two points must be close to grid lines of the computational grid
    (the maximum distance is one hundredth of the length of the straight line).

    Parameters
    ----------
    model_type: Literal["segmentxy"]
        Model type discriminator.
    points: list[tuple[float, float]]
        Pairs of (x, y) values to define the segment.
    float_format: str
        The format to use for the floats in the points.

    """

    model_type: Literal["segmentxy"] = "segmentxy"
    points: list[tuple[float, float]]
    float_format: str = "0.8f"

    def cmd(self) -> str:
        repr = f"SEGMENT XY &"
        for point in self.points:
            repr += (
                f"\n\t{point[0]:{self.float_format}} {point[1]:{self.float_format}} &"
            )
        return repr + "\n\t"


class SEGMENTIJ(BaseSubComponent):
    """SWAN SEGMENT IJ BOUNDSPEC subcomponent.

    `SEGMENT IJ < [i] [j] >`

    The segment is defined by means of a series of computational grid points given in
    terms of grid indices (origin at 0,0); not all grid points on the segment have to
    be mentioned. If two points are on the same grid line, intermediate points are
    assumed to be on the segment as well.

    Parameters
    ----------
    model_type: Literal["segmentij"]
        Model type discriminator.
    points: list[tuple[int, int]]
        Pairs of (i, j) values to define the segment.

    """

    model_type: Literal["segmentxy"] = "segmentxy"
    points: list[tuple[int, int]]

    def cmd(self) -> str:
        repr = f"SEGMENT IJ &"
        for point in self.points:
            repr += f"\n\t{point[0]} {point[1]} &"
        return repr + "\n\t"


class PAR(BaseSubComponent):
    """Parameter subcomponent.

    `PAR [hs] [per] [dir] [dd]`

    Parameters
    ----------
    model_type: Literal["par"]
        Model type discriminator.
    hs: float
        The significant wave height (m).
    per: float
        The characteristic period (s) of the energy spectrum (relative frequency; which
        is equal to absolute frequency in the absence of currents); `per` is the value
        of the peak period if option PEAK is chosen in command BOUND SHAPE or `per` is
        the value of the mean period, if option MEAN was chosen in command BOUND SHAPE.
    dir: float
        The peak wave direction θpeak (degrees), constant over frequencies.
    dd: float
        Coefficient of directional spreading; a $cos^m(θ)$ distribution is assumed.
        `dd` is interpreted as the directional standard deviation in degrees, if the
        option DEGREES is chosen in the command BOUND SHAPE. Default: `dd=30`.
        `dd` is interpreted as the power `m`, if the option POWER is chosen in the
        command BOUND SHAPE. Default: `dd=2`.

    """

    model_type: Literal["par"] = "par"
    hs: confloat(gt=0.0)
    per: confloat(gt=0.0)
    dir: confloat(ge=-360.0, le=360.0)
    dd: confloat(ge=0.0, le=360.0)

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        return f"PAR hs={self.hs} per={self.per} dir={self.dir} dd={self.dd}"


class CONSTANTPAR(PAR):
    """Constant parameter subcomponent.

    `CONSTANT PAR [hs] [per] [dir] [dd]`

    """

    model_type: Literal["constantpar"] = "constantpar"

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        return f"CONSTANT {super().cmd()}"


class VARIABLEPAR(BaseSubComponent):
    """Variable parameter subcomponent.

    `VARIABLE PAR < [len] [hs] [per] [dir] [dd] >`

    Parameters
    ----------
    model_type: Literal["variablepar"]
        Model type discriminator.
    hs: List[float]
        The significant wave height (m).
    per: List[float]
        The characteristic period (s) of the energy spectrum (relative frequency; which
        is equal to absolute frequency in the absence of currents); `per` is the value
        of the peak period if option PEAK is chosen in command BOUND SHAPE or `per` is
        the value of the mean period, if option MEAN was chosen in command BOUND SHAPE.
    dir: List[float]
        The peak wave direction θpeak (degrees), constant over frequencies.
    dd: List[float]
        Coefficient of directional spreading; a $cos^m(θ)$ distribution is assumed.
        `dd` is interpreted as the directional standard deviation in degrees, if the
        option DEGREES is chosen in the command BOUND SHAPE. Default: `dd=30`.
        `dd` is interpreted as the power `m`, if the option POWER is chosen in the
        command BOUND SHAPE. Default: `dd=2`.
    dist: Optional[list[float]]
        Is the distance from the first point of the side or segment to the point along
        the side or segment for which the incident wave spectrum is prescribed.
        Note: these points do no have to coincide with grid points of the computational
        grid. `len` is the distance in m or degrees in the case of spherical
        coordinates, not in grid steps. The values of `len` should be given
        in ascending order. The length along a SIDE is measured in clockwise or
        counterclockwise direction, depending on the options CCW or CLOCKWISE (see
        above). The option CCW is default. In case of a SEGMENT the length is
        measured from the indicated begin point of the segment.

    """

    model_type: Literal["variablepar"] = "variablepar"
    hs: list[confloat(ge=0.0)]
    per: list[confloat(ge=0.0)]
    dir: list[confloat(ge=-360.0, le=360.0)]
    dd: list[confloat(ge=0.0, le=360.0)]
    dist: list[confloat(ge=0)]

    @root_validator
    def ensure_equal_size(cls, values):
        for key in ["hs", "per", "dir", "dd"]:
            if len(values[key]) != len(values["dist"]):
                raise ValueError(f"Sizes of dist and {key} must be the size")
        return values

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        repr = "VARIABLE PAR"
        for dist, hs, per, dir, dd in zip(
            self.dist, self.hs, self.per, self.dir, self.dd
        ):
            repr += f" &\n\t\tlen={dist} hs={hs} per={per} dir={dir} dd={dd}"
        return repr


class CONSTANTFILE(BaseSubComponent):
    """Constant file subcomponent.

    `CONSTANT FILE 'fname' [seq]`

    Parameters
    ----------
    model_type: Literal["constantfile"]
        Model type discriminator.
    fname: str
        Name of the file containing the boundary condition.
    seq: float
        sequence number of geographic location in the file (see Appendix D);
        useful for files which contain spectra for more than one location.
        Note: a TPAR file always contains only one location so in this case
        [seq] must always be 1.

    Note
    ----
    There are three types of files:
    - TPAR files containing nonstationary wave parameters.
    - files containing stationary or nonstationary 1D spectra
      (usually from measurements).
    - files containing stationary or nonstationary 2D spectra
      (from other computer programs or other SWAN runs).
    A TPAR file is for only one location; it has the string TPAR on the first
    line of the file and a number of lines which each contain 5 numbers, i.e.:
    Time (ISO-notation), Hs, Period (average or peak period depending on the
    choice given in command BOUND SHAPE), Peak Direction (Nautical or Cartesian,
    depending on command SET), Directional spread (in degrees or as power of cos
    depending on the choice given in command BOUND SHAPE).

    Example of a TPAR file
    ----------------------
    TPAR
    19920516.130000 4.2 12. -110. 22.
    19920516.180000 4.2 12. -110. 22.
    19920517.000000 1.2 8. -110. 22.
    19920517.120000 1.4 8.5 -80. 26
    19920517.200000 0.9 6.5 -95. 28

    """

    model_type: Literal["constantfile"] = "constantfile"
    fname: constr(max_length=40)
    seq: Optional[conint(ge=1)]

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        repr = f"CONSTANT FILE fname='{self.fname}'"
        if self.seq is not None:
            repr += f" seq={self.seq}"
        return repr


class VARIABLEFILE(BaseSubComponent):
    """Variable file subcomponent.

    `VARIABLE FILE < [len] 'fname' [seq] >`

    Parameters
    ----------
    model_type: Literal["variablefile"]
        Model type discriminator.
    fname: list
        Names of the file containing the boundary condition.
    seq: Optional[list]
        sequences number of geographic location in the file (see Appendix D);
        useful for files which contain spectra for more than one location.
        Note: a TPAR file always contains only one location so in this case
        `seq` must always be 1.
    dist: Optional[list[float]]
        Is the distance from the first point of the side or segment to the point along
        the side or segment for which the incident wave spectrum is prescribed.
        Note: these points do no have to coincide with grid points of the computational
        grid. `len` is the distance in m or degrees in the case of spherical
        coordinates, not in grid steps. The values of `len` should be given
        in ascending order. The length along a SIDE is measured in clockwise or
        counterclockwise direction, depending on the options CCW or CLOCKWISE (see
        above). The option CCW is default. In case of a SEGMENT the length is
        measured from the indicated begin point of the segment.

    Note
    ----
    There are three types of files:
    - TPAR files containing nonstationary wave parameters.
    - files containing stationary or nonstationary 1D spectra
      (usually from measurements).
    - files containing stationary or nonstationary 2D spectra
      (from other computer programs or other SWAN runs).
    A TPAR file is for only one location; it has the string TPAR on the first
    line of the file and a number of lines which each contain 5 numbers, i.e.:
    Time (ISO-notation), Hs, Period (average or peak period depending on the
    choice given in command BOUND SHAPE), Peak Direction (Nautical or Cartesian,
    depending on command SET), Directional spread (in degrees or as power of cos
    depending on the choice given in command BOUND SHAPE).

    Example of a TPAR file
    ----------------------
    TPAR
    19920516.130000 4.2 12. -110. 22.
    19920516.180000 4.2 12. -110. 22.
    19920517.000000 1.2 8. -110. 22.
    19920517.120000 1.4 8.5 -80. 26
    19920517.200000 0.9 6.5 -95. 28

    """

    model_type: Literal["variablefile"] = "variablefile"
    fname: list[constr(max_length=40)]
    seq: Optional[list[conint(ge=1)]]
    dist: list[confloat(ge=0)]

    @root_validator
    def ensure_equal_size(cls, values):
        for key in ["fname", "seq"]:
            if values.get(key) is not None and len(values[key]) != len(values["dist"]):
                raise ValueError(f"Sizes of dist and {key} must be the size")
        if values.get("seq") is None:
            values["seq"] = [1] * len(values["dist"])
        return values

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        repr = "VARIABLE FILE"
        for dist, fname, seq in zip(self.dist, self.fname, self.seq):
            repr += f" &\n\t\tlen={dist} fname='{fname}' seq={seq}"
        return repr


class DEFAULT(BaseSubComponent):
    """Default initial conditions subcomponent.

    `DEFAULT`

    Parameters
    ----------
    model_type: Literal["default"]
        Model type discriminator.

    The initial spectra are computed from the local wind velocities, using the
    deep-water growth curve of Kahma and Calkoen (1992), cut off at values of
    significant wave height and peak frequency from Pierson and Moskowitz (1964).
    The average (over the model area) spatial step size is used as fetch with local
    wind. The shape of the spectrum is default JONSWAP with a cos2-directional
    distribution (options are available: see command BOUND SHAPE).

    """

    model_type: Literal["default"] = "default"


class ZERO(BaseSubComponent):
    """ZERO initial conditions subcomponent.

    `ZERO`

    Parameters
    ----------
    model_type: Literal["zero"]
        Model type discriminator.

    The initial spectral densities are all 0; note that if waves are generated in the
    model only by wind, waves can become non-zero only by the presence of the
    ”A” term in the growth model; see the keyword AGROW in command GEN3.

    """

    model_type: Literal["zero"] = "zero"


class HOTSINGLE(BaseSubComponent):
    """SWAN Hotstart single subcomponent.

    `HOTSTART SINGLE fname='fname' FREE|UNFORMATTED`

    parameters
    ----------
    model_type: Literal["hotsingle"]
        Model type discriminator.
    fname: str
        Name of the file containing the initial wave field.
    format: Literal["free", "unformatted"]
        Format of the file containing the initial wave field.
        - FREE: free format.
        - UNFORMATTED: binary format.

    Initial wave field is read from file; this file was generated in a previous SWAN
    run by means of the HOTFILE command. If the previous run was nonstationary,
    the time found on the file will be assumed to be the initial time of computation. It
    can also be used for stationary computation as first guess. The computational grid
    (both in geographical space and in spectral space) must be identical to the one in
    the run in which the initial wave field was computed

    Input will be read from a single (concatenated) hotfile. In the case of a previous
    parallel MPI run, the concatenated hotfile can be created from a set of multiple
    hotfiles using the program hcat.exe, see Implementation Manual.

    """

    model_type: Literal["hotsingle"] = "hotsingle"
    fname: constr(max_length=85)
    format: Literal["free", "unformatted"] = "free"

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        return f"HOTSTART SINGLE fname='{self.fname}' {self.format.upper()}"


class HOTMULTIPLE(BaseSubComponent):
    """SWAN Hotstart multiple subcomponent.

    parameters
    ----------
    model_type: Literal["hotmultiple"]
        Model type discriminator.
    fname: str
        Name of the file containing the boundary condition.
    format: Literal["free", "unformatted"]
        Format of the file containing the initial wave field.
        - FREE: free format.
        - UNFORMATTED: binary format.

    Initial wave field is read from file; this file was generated in a previous SWAN
    run by means of the HOTFILE command. If the previous run was nonstationary,
    the time found on the file will be assumed to be the initial time of computation. It
    can also be used for stationary computation as first guess. The computational grid
    (both in geographical space and in spectral space) must be identical to the one in
    the run in which the initial wave field was computed

    Input will be read from multiple hotfiles obtained from a previous parallel MPI run.
    The number of files equals the number of processors. Hence, for the present run the
    same number of processors must be chosen.

    """

    model_type: Literal["hotmultiple"] = "hotmultiple"
    fname: constr(max_length=85)
    format: Literal["free", "unformatted"] = "free"

    def cmd(self) -> str:
        """Render subcomponent cmd."""
        return f"HOTSTART MULTIPLE fname='{self.fname}' {self.format.upper()}"