__version__ = "1.0"

import json
import os

from meshroom.core import desc


class DividedInputNodeSize(desc.DynamicNodeSize):
    """
    The LDR2HDR will reduce the amount of views in the SfMData.
    This class converts the number of LDR input views into the number of HDR output views.
    """
    def __init__(self, param, divParam):
        super(DividedInputNodeSize, self).__init__(param)
        self._divParam = divParam
    def computeSize(self, node):
        s = super(DividedInputNodeSize, self).computeSize(node)
        divParam = node.attribute(self._divParam)
        return s / divParam.value


class LDRToHDR(desc.CommandLineNode):
    commandLine = 'aliceVision_convertLDRToHDR {allParams}'
    size = DividedInputNodeSize('input', 'groupSize')

    inputs = [
        desc.File(
            name='input',
            label='Input',
            description="SfM Data File",
            value='',
            uid=[0],
        ),
        desc.IntParam(
            name='groupSize',
            label='Exposure bracket count',
            description='Number of exposure brackets used per HDR image',
            value=3,
            range=(0, 10, 1),
            uid=[0]
        ),
        desc.FloatParam(
            name='highlightCorrectionFactor',
            label='Highlights correction',
            description='Pixels saturated in all input images have a partial information about their real luminance.\n'
                        'We only know that the value should be >= to the standard hdr fusion.\n'
                        'This parameters allows to perform a post-processing step to put saturated pixels to a constant '
                        'value defined by the `highlightsMaxLuminance` parameter.\n'
                        'This parameter is float to enable to weight this correction.',
            value=1.0,
            range=(0.0, 1.0, 0.01),
            uid=[0],
        ),
        desc.FloatParam(
            name='highlightTargetLux',
            label='Highlight Target Luminance (Lux)',
            description='This is an arbitrary target value (in Lux) used to replace the unknown luminance value of the saturated pixels.\n'
                        '\n'
                        'Some Outdoor Reference Light Levels:\n'
                        ' * 120,000 lux : Brightest sunlight\n'
                        ' * 110,000 lux : Bright sunlight\n'
                        ' * 20,000 lux : Shade illuminated by entire clear blue sky, midday\n'
                        ' * 1,000 lux : Typical overcast day, midday\n'
                        ' * 400 lux : Sunrise or sunset on a clear day\n'
                        ' * 40 lux : Fully overcast, sunset/sunrise\n'
                        '\n'
                        'Some Indoor Reference Light Levels:\n'
                        ' * 20000 lux : Max Usually Used Indoor\n'
                        ' * 750 lux : Supermarkets\n'
                        ' * 500 lux : Office Work\n'
                        ' * 150 lux : Home\n',
            value=120000.0,
            range=(1000.0, 150000.0, 1.0),
            uid=[0],
        ),
        desc.BoolParam(
            name='fisheyeLens',
            label='Fisheye Lens',
            description="Enable if a fisheye lens has been used.\n "
                        "This will improve the estimation of the Camera's Response Function by considering only the pixels in the center of the image\n"
                        "and thus ignore undefined/noisy pixels outside the circle defined by the fisheye lens.",
            value=False,
            uid=[0],
        ),
        desc.BoolParam(
            name='calibrationRefineExposures',
            label='Refine Exposures',
            description="Refine exposures provided by metadata (shutter speed, f-number, iso). Only available for 'laguerre' calibration method.",
            value=False,
            uid=[0],
        ),
        desc.BoolParam(
            name='byPass',
            label='bypass convert',
            description="Bypass HDR creation and use the medium bracket as the source for the next steps",
            value=False,
            uid=[0],
        ),
        desc.ChoiceParam(
            name='calibrationMethod',
            label='Calibration Method',
            description="Method used for camera calibration \n"
                        " * linear \n"
                        " * robertson \n"
                        " * debevec \n"
                        " * grossberg \n"
                        " * laguerre",
            values=['linear', 'robertson', 'debevec', 'grossberg', 'laguerre'],
            value='debevec',
            exclusive=True,
            uid=[0],
        ),
        desc.ChoiceParam(
            name='calibrationWeight',
            label='Calibration Weight',
            description="Weight function used to calibrate camera response \n"
                        " * default (automatically selected according to the calibrationMethod) \n"
                        " * gaussian \n"
                        " * triangle \n"
                        " * plateau",
            value='default',
            values=['default', 'gaussian', 'triangle', 'plateau'],
            exclusive=True,
            uid=[0],
        ),
        desc.ChoiceParam(
            name='fusionWeight',
            label='Fusion Weight',
            description="Weight function used to fuse all LDR images together \n"
                        " * gaussian \n"
                        " * triangle \n"
                        " * plateau",
            value='gaussian',
            values=['gaussian', 'triangle', 'plateau'],
            exclusive=True,
            uid=[0],
        ),
        desc.IntParam(
            name='calibrationNbPoints',
            label='Calibration Nb Points',
            description='Internal number of points used for calibration.',
            value=0,
            range=(0, 10000000, 1000),
            uid=[0],
            advanced=True,
        ),
        desc.IntParam(
            name='calibrationDownscale',
            label='Calibration Downscale',
            description='Scaling factor applied to images before calibration of the response function to reduce the impact of misalignment.',
            value=4,
            range=(1, 16, 1),
            uid=[0],
            advanced=True,
        ),
        desc.IntParam(
            name='channelQuantizationPower',
            label='Channel Quantization Power',
            description='Quantization level like 8 bits or 10 bits.',
            value=10,
            range=(8, 14, 1),
            uid=[0],
            advanced=True,
        ),
        desc.ChoiceParam(
            name='verboseLevel',
            label='Verbose Level',
            description='Verbosity level (fatal, error, warning, info, debug, trace).',
            value='info',
            values=['fatal', 'error', 'warning', 'info', 'debug', 'trace'],
            exclusive=True,
            uid=[],
        ),
    ]

    outputs = [
        desc.File(
            name='outSfMDataFilename',
            label='Output SfMData File',
            description='Path to the output sfmdata file',
            value=desc.Node.internalFolder + 'sfmData.abc',
            uid=[],
        )
    ]
