package macro;

import star.mdx.MdxMacro;
import star.mdx.MdxProject;
import star.mdx.MdxDesignStudy;
import star.mdx.MdxStudyParameterManager;
import star.mdx.MdxStudyParameter;
import star.mdx.MdxStudyParameterBase;
import static star.mdx.MdxStudyParameterBase.ParameterType;
import star.mdx.MdxContinuousParameterValue;
import star.mdx.MdxConstantParameterValue;
import star.mdx.MdxSuccessfulDesignSet;
import star.mdx.MdxDesignSetManager;
import star.mdx.MdxDesignSet;

import star.common.Units;
import star.common.UnitsManager;
import star.common.ScalarPhysicalQuantity;

public class RunStudyWithParameters extends MdxMacro {
  private final String MIN_PREFIX = "min:";
  private final String MAX_PREFIX = "max:";
  private final String INCREMENT_PREFIX = "inc:";
  private final String UNITS_PREFIX = "units:";
  private final String CONSTANT_PREFIX = "const:";
  
  MdxStudyParameterManager parameterManager;
  UnitsManager unitsManager;

  public void execute() {
    MdxDesignStudy designStudy = getDesignStudy();

    // clear prior design study state
    designStudy.clearDesignStudy();

    // set passed parameter values/ranges
    parameterManager = designStudy.getStudyParameters();
    setContinuousParameters();
    setConstantParameters();

    // run design study
    designStudy.runDesignStudy();

    // save study outputs to CSV
    // TODO: have design set be configurable?
    MdxDesignSetManager designSetManager = designStudy.getDesignSets();
    MdxDesignSet designSet = designSetManager.getDesignSet("Successful");
    saveStudyData(designSet);
  }

  private MdxDesignStudy getDesignStudy() {
    MdxProject project = getActiveMdxProject();
    unitsManager = project.getUnitsManager();

    // obtain design study name from JVM property, since we can't pass parameters otherwise
    String studyName = System.getProperty("studyName");

    return project.getDesignStudyManager().getDesignStudy(studyName);
  }

  private void setContinuousParameters() {
    String passedParameters = System.getProperty("continuousParameters");

    if (passedParameters != null) {
      for (String parameterName : passedParameters.split(",")) {
        setContinuousParameter(parameterName);
      }
    }
  }

  private void setConstantParameters() {
    String passedParameters = System.getProperty("constantParameters");

    if (passedParameters != null) {
      for (String parameterName : passedParameters.split(",")) {
        setConstantParameter(parameterName);
      }
    }
  }

  private void setContinuousParameter(String parameterName) {
    // parse continuous parameter properties
    double minValue = getDoubleProperty(MIN_PREFIX + parameterName);
    double maxValue = getDoubleProperty(MAX_PREFIX + parameterName);
    double incrementValue = getDoubleProperty(INCREMENT_PREFIX + parameterName);

    // including units
    Units units = getUnitsForParameter(parameterName);

    // get parameter value reference from project
    MdxStudyParameter parameter = (MdxStudyParameter) getParameterOfType(parameterName, ParameterType.CONTINUOUS);
    MdxContinuousParameterValue parameterValue = parameter.getContinuousParameterValue();

    // set parsed properties
    ScalarPhysicalQuantity minimum = parameterValue.getMinimumQuantity();
    minimum.setValueAndUnits(minValue, units);

    ScalarPhysicalQuantity maximum = parameterValue.getMaximumQuantity();
    maximum.setValueAndUnits(maxValue, units);

    ScalarPhysicalQuantity increment = parameterValue.getIncrementQuantity();
    increment.setValueAndUnits(incrementValue, units);
  }

  private void setConstantParameter(String parameterName) {
    // get parameter value & units from JVM properties
    double constValue = getDoubleProperty(CONSTANT_PREFIX + parameterName);
    Units units = getUnitsForParameter(parameterName);

    // ensure we're working with a constant parameter
    MdxStudyParameter parameter = (MdxStudyParameter) getParameterOfType(parameterName, ParameterType.CONSTANT);
    MdxConstantParameterValue parameterValue = parameter.getConstantParameterValue();
    
    // set value and units of constant parameter
    ScalarPhysicalQuantity baseline = parameterValue.getBaselineQuantity();
    baseline.setValueAndUnits(constValue, units);
  }

  private void saveStudyData(MdxDesignSet designSet) {
    String outFileName = System.getProperty("outFile", "drag_data.csv");
    String outPath = resolvePath(outFileName);

    designSet.exportCsvFile(outPath);
  }

  private double getDoubleProperty(String propertyName) {
    // TODO: handle invalid double case
    String rawValue = System.getProperty(propertyName);

    return Double.parseDouble(rawValue);
  }

  private Units getUnitsForParameter(String parameterName) {
    // fetch units, defaulting to unitless (empty unit string)
    String unitName = System.getProperty(UNITS_PREFIX + parameterName, "");

    // fetch Units instance from unit manager
    Units units = unitsManager.getUnits(unitName);

    return units;
  }

  private MdxStudyParameterBase getParameterOfType(String parameterName, ParameterType paramType) {
    MdxStudyParameterBase parameter = parameterManager.getStudyParameterBase(parameterName);

    // set parameter type as necessary
    if (parameter.getParameterType() != paramType) {
      parameter.setParameterType(paramType);
    }

    return parameter;
  }
}
